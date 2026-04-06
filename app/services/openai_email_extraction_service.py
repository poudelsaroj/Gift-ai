"""OpenAI-backed structured extraction for email gift ingestion."""

from __future__ import annotations

import json
import time
from typing import Any

import httpx

from app.core.config import get_settings
from app.services.email_types import ParsedAttachment, ParsedEmail


class OpenAIEmailExtractionService:
    """Use the Responses API to classify gift emails and extract canonical gift JSON."""

    _SUPPORTED_CODE_INTERPRETER_EXTENSIONS = {".csv", ".pdf", ".txt", ".tsv", ".xlsx"}
    _MAX_RETRIES = 3

    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = settings.openai_api_key
        self.base_url = settings.openai_base_url.rstrip("/")
        self.model = settings.openai_gift_extraction_model

    def extract(
        self,
        *,
        email: ParsedEmail,
        source_system: str,
    ) -> dict[str, Any]:
        """Classify an email and extract canonical gift records."""
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI-backed email extraction.")

        uploaded_file_ids: list[str] = []
        unsupported_attachments: list[dict[str, Any]] = []
        content = [
            {
                "type": "input_text",
                "text": self._build_user_prompt(
                    email=email,
                    source_system=source_system,
                    unsupported_attachments=unsupported_attachments,
                ),
            }
        ]
        tools: list[dict[str, Any]] = []

        for attachment in email.attachments:
            extension = self._extension(attachment.filename)
            if extension in self._SUPPORTED_CODE_INTERPRETER_EXTENSIONS:
                file_id = self._upload_file(attachment=attachment)
                uploaded_file_ids.append(file_id)
                content.append({"type": "input_file", "file_id": file_id})
            else:
                unsupported_attachments.append(
                    {
                        "filename": attachment.filename,
                        "mime_type": attachment.mime_type,
                        "size": attachment.size,
                    }
                )

        if uploaded_file_ids:
            tools.append({"type": "code_interpreter", "container": {"type": "auto"}})

        try:
            response = self._create_response(
                content=content,
                tools=tools,
                schema=self._response_schema(),
            )
        finally:
            for file_id in uploaded_file_ids:
                self._delete_file(file_id)

        parsed = self._parse_json_response(response)
        parsed.setdefault("unsupported_attachments", unsupported_attachments)
        return parsed

    def _create_response(
        self,
        *,
        content: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        schema: dict[str, Any],
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "input": [
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": self._system_prompt()}],
                },
                {
                    "role": "user",
                    "content": content,
                },
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "gmail_gift_extraction",
                    "schema": schema,
                    "strict": True,
                }
            },
        }
        if tools:
            payload["tools"] = tools

        last_error: Exception | None = None
        for attempt in range(1, self._MAX_RETRIES + 1):
            try:
                with httpx.Client(timeout=120.0) as client:
                    response = client.post(
                        f"{self.base_url}/responses",
                        headers=self._headers(),
                        json=payload,
                    )
                    try:
                        response.raise_for_status()
                    except httpx.HTTPStatusError as exc:
                        detail = self._response_error_detail(response)
                        raise ValueError(
                            f"OpenAI Responses API request failed with status {response.status_code}: {detail}"
                        ) from exc
                    return response.json()
            except (httpx.RemoteProtocolError, httpx.ReadTimeout, httpx.ConnectError) as exc:
                last_error = exc
                if attempt >= self._MAX_RETRIES:
                    break
                time.sleep(1.5 * attempt)
        raise ValueError(
            "OpenAI Responses API request failed after retries: "
            f"{type(last_error).__name__ if last_error else 'unknown error'}"
        ) from last_error

    def _upload_file(self, *, attachment: ParsedAttachment) -> str:
        files = {
            "file": (
                attachment.filename,
                attachment.data,
                attachment.mime_type or "application/octet-stream",
            )
        }
        data = {"purpose": "user_data"}
        last_error: Exception | None = None
        payload: dict[str, Any] | None = None
        for attempt in range(1, self._MAX_RETRIES + 1):
            try:
                with httpx.Client(timeout=120.0) as client:
                    response = client.post(
                        f"{self.base_url}/files",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        data=data,
                        files=files,
                    )
                    try:
                        response.raise_for_status()
                    except httpx.HTTPStatusError as exc:
                        detail = self._response_error_detail(response)
                        raise ValueError(
                            f"OpenAI file upload failed with status {response.status_code}: {detail}"
                        ) from exc
                    payload = response.json()
                    break
            except (httpx.RemoteProtocolError, httpx.ReadTimeout, httpx.ConnectError) as exc:
                last_error = exc
                if attempt >= self._MAX_RETRIES:
                    break
                time.sleep(1.5 * attempt)
        if payload is None:
            raise ValueError(
                "OpenAI file upload failed after retries: "
                f"{type(last_error).__name__ if last_error else 'unknown error'}"
            ) from last_error
        file_id = payload.get("id")
        if not isinstance(file_id, str) or not file_id:
            raise ValueError("OpenAI file upload did not return a valid file id.")
        return file_id

    def _delete_file(self, file_id: str) -> None:
        try:
            with httpx.Client(timeout=30.0) as client:
                client.delete(
                    f"{self.base_url}/files/{file_id}",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
        except Exception:
            return

    def _parse_json_response(self, payload: dict[str, Any]) -> dict[str, Any]:
        output_text = payload.get("output_text")
        if isinstance(output_text, str) and output_text.strip():
            return json.loads(output_text)

        for item in payload.get("output") or []:
            if not isinstance(item, dict):
                continue
            for content in item.get("content") or []:
                if not isinstance(content, dict):
                    continue
                text = content.get("text")
                if isinstance(text, str) and text.strip():
                    return json.loads(text)
        raise ValueError("OpenAI extraction response did not contain structured JSON text.")

    def _response_error_detail(self, response: httpx.Response) -> str:
        text = response.text.strip()
        if not text:
            return "empty response body"
        return text[:500]

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _system_prompt(self) -> str:
        return (
            "You are extracting nonprofit gift data from emails and attachments. "
            "Return strict JSON matching the schema. "
            "If the email is not about a donation, grant, contribution, pledge, match, "
            "or gift record, set is_gift_email to false and return an empty gifts array. "
            "When gifts are present, normalize them into the canonical record shape. "
            "Do not invent values. Use null when unknown. "
            "Create one record per distinct gift transaction or row. "
            "Use ISO dates like YYYY-MM-DD. Amounts must be decimal strings like 125.00."
        )

    def _build_user_prompt(
        self,
        *,
        email: ParsedEmail,
        source_system: str,
        unsupported_attachments: list[dict[str, Any]],
    ) -> str:
        body_text = email.body_text or ""
        return (
            f"Source system: {source_system}\n"
            f"Email subject: {email.subject or ''}\n"
            f"From name: {email.from_name or ''}\n"
            f"From email: {email.from_email or ''}\n"
            f"To email: {email.to_email or ''}\n"
            f"Message id: {email.message_id}\n"
            f"Thread id: {email.thread_id or ''}\n"
            f"Internal date: {email.internal_date.isoformat() if email.internal_date else ''}\n"
            f"Labels: {', '.join(email.labels)}\n"
            f"Snippet: {email.snippet or ''}\n"
            "Email text follows.\n"
            f"{body_text}\n\n"
            "Attachments are included separately when supported. "
            f"Unsupported attachment metadata: {json.dumps(unsupported_attachments)}\n"
            "Return final canonical gift records only."
        )

    def _extension(self, filename: str) -> str:
        lowered = (filename or "").lower()
        if "." not in lowered:
            return ""
        return lowered[lowered.rfind(".") :]

    def _response_schema(self) -> dict[str, Any]:
        gift_schema = {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "recordType",
                "sourceRecordId",
                "sourceParentId",
                "giftId",
                "sourceFileId",
                "primaryName",
                "primaryEmail",
                "donorName",
                "donorEmail",
                "companyName",
                "amount",
                "currency",
                "recordDate",
                "giftDate",
                "paymentType",
                "giftType",
                "campaignId",
                "campaignName",
                "relatedEntityId",
                "relatedEntityName",
                "receiptNumber",
                "memo",
                "confidenceScore",
                "sourceMedium",
                "sourceFilename",
                "sourceAttachmentId",
                "messageId",
            ],
            "properties": {
                "recordType": {"type": ["string", "null"]},
                "sourceRecordId": {"type": ["string", "null"]},
                "sourceParentId": {"type": ["string", "null"]},
                "giftId": {"type": ["string", "null"]},
                "sourceFileId": {"type": ["string", "null"]},
                "primaryName": {"type": ["string", "null"]},
                "primaryEmail": {"type": ["string", "null"]},
                "donorName": {"type": ["string", "null"]},
                "donorEmail": {"type": ["string", "null"]},
                "companyName": {"type": ["string", "null"]},
                "amount": {"type": ["string", "null"]},
                "currency": {"type": ["string", "null"]},
                "recordDate": {"type": ["string", "null"]},
                "giftDate": {"type": ["string", "null"]},
                "paymentType": {"type": ["string", "null"]},
                "giftType": {"type": ["string", "null"]},
                "campaignId": {"type": ["string", "null"]},
                "campaignName": {"type": ["string", "null"]},
                "relatedEntityId": {"type": ["string", "null"]},
                "relatedEntityName": {"type": ["string", "null"]},
                "receiptNumber": {"type": ["string", "null"]},
                "memo": {"type": ["string", "null"]},
                "confidenceScore": {"type": ["number", "null"]},
                "sourceMedium": {"type": ["string", "null"]},
                "sourceFilename": {"type": ["string", "null"]},
                "sourceAttachmentId": {"type": ["string", "null"]},
                "messageId": {"type": ["string", "null"]},
            },
        }
        return {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "is_gift_email",
                "extraction_summary",
                "gifts",
                "unsupported_attachments",
            ],
            "properties": {
                "is_gift_email": {"type": "boolean"},
                "extraction_summary": {"type": ["string", "null"]},
                "gifts": {"type": "array", "items": gift_schema},
                "unsupported_attachments": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["filename", "mime_type", "size"],
                        "properties": {
                            "filename": {"type": ["string", "null"]},
                            "mime_type": {"type": ["string", "null"]},
                            "size": {"type": ["number", "null"]},
                        },
                    },
                },
            },
        }
