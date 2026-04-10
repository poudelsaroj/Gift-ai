"""OpenAI-backed canonical gift extraction for uploaded tabular files."""

from __future__ import annotations

import json
import time
from typing import Any

import httpx

from app.core.config import get_settings
from app.models.source_config import SourceConfig
from app.services.structured_tabular_import_service import StructuredTabularImportService


class OpenAITabularImportService:
    """Use the Responses API + file uploads to normalize CSV/XLSX gift files."""

    _SUPPORTED_EXTENSIONS = {".csv", ".tsv", ".xlsx"}
    _MAX_RETRIES = 3

    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = settings.openai_api_key
        self.base_url = settings.openai_base_url.rstrip("/")
        self.model = settings.openai_gift_extraction_model
        self.structured_import_service = StructuredTabularImportService()

    def extract(
        self,
        *,
        content: bytes,
        filename: str,
        content_type: str | None,
        source: SourceConfig,
    ) -> dict[str, Any]:
        """Upload the file to OpenAI and return canonical gift JSON."""
        structured_extraction = self.structured_import_service.extract(
            content=content,
            filename=filename,
            source=source,
        )
        if structured_extraction is not None:
            return structured_extraction
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI-backed file imports.")
        extension = self._extension(filename)
        if extension not in self._SUPPORTED_EXTENSIONS:
            raise ValueError("Upload a supported CSV, TSV, or XLSX file.")

        file_id = self._upload_file(content=content, filename=filename, content_type=content_type)
        try:
            response = self._create_response(
                file_id=file_id,
                prompt=self._build_user_prompt(source=source, filename=filename),
                schema=self._response_schema(),
            )
        finally:
            self._delete_file(file_id)

        return self._parse_json_response(response)

    def _create_response(self, *, file_id: str, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "input": [
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": self._system_prompt()}],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {"type": "input_file", "file_id": file_id},
                    ],
                },
            ],
            "tools": [{"type": "code_interpreter", "container": {"type": "auto"}}],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "tabular_gift_import",
                    "schema": schema,
                    "strict": True,
                }
            },
        }

        last_error: Exception | None = None
        for attempt in range(1, self._MAX_RETRIES + 1):
            try:
                with httpx.Client(timeout=180.0) as client:
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
                            f"OpenAI tabular import failed with status {response.status_code}: {detail}"
                        ) from exc
                    return response.json()
            except (httpx.RemoteProtocolError, httpx.ReadTimeout, httpx.ConnectError) as exc:
                last_error = exc
                if attempt >= self._MAX_RETRIES:
                    break
                time.sleep(1.5 * attempt)
        raise ValueError(
            "OpenAI tabular import failed after retries: "
            f"{type(last_error).__name__ if last_error else 'unknown error'}"
        ) from last_error

    def _upload_file(self, *, content: bytes, filename: str, content_type: str | None) -> str:
        files = {
            "file": (
                filename,
                content,
                content_type or "application/octet-stream",
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
        raise ValueError("OpenAI tabular import response did not contain structured JSON text.")

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _response_error_detail(self, response: httpx.Response) -> str:
        text = response.text.strip()
        if not text:
            return "empty response body"
        return text[:500]

    def _system_prompt(self) -> str:
        return (
            "You extract nonprofit gift data from uploaded spreadsheets. "
            "Return strict JSON matching the schema. "
            "Only include rows that clearly describe gifts, donations, grants, pledges, matching gifts, ACHs, checks, or wires. "
            "Normalize each distinct gift row into the canonical record shape. "
            "For CSV or spreadsheet files with multiple gift rows, return one gift object per row in the same order as the file. "
            "When the file does not contain a stable source id, use sequential row-based ids like '1', '2', '3' for both sourceRecordId and giftId. "
            "Do not invent values. Use null when unknown. "
            "Amounts must be decimal strings like 125.00. "
            "Dates must be ISO YYYY-MM-DD when derivable."
        )

    def _build_user_prompt(self, *, source: SourceConfig, filename: str) -> str:
        return (
            f"Source name: {source.source_name}\n"
            f"Source system: {source.source_system}\n"
            f"Filename: {filename}\n"
            "Read the uploaded tabular file and identify the gift rows. "
            "If the file contains multiple rows, return one gift object per row. "
            "Use sequential row-based ids when no stable source record id exists in the file. "
            "Return final canonical gift records only."
        )

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
            "required": ["is_gift_file", "summary", "gifts"],
            "properties": {
                "is_gift_file": {"type": "boolean"},
                "summary": {"type": ["string", "null"]},
                "gifts": {"type": "array", "items": gift_schema},
            },
        }

    def _extension(self, filename: str) -> str:
        lowered = (filename or "").lower()
        if "." not in lowered:
            return ""
        return lowered[lowered.rfind(".") :]
