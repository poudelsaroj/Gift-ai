"""Reusable email parsing and OpenAI-backed gift extraction helpers."""

from __future__ import annotations

import base64
import hashlib
import re
from datetime import UTC, datetime
from html.parser import HTMLParser
from typing import Any

from app.connectors.base.types import RawFetchItem
from app.models.source_config import SourceConfig
from app.services.email_types import ParsedAttachment, ParsedEmail
from app.services.openai_email_extraction_service import OpenAIEmailExtractionService


class _HtmlToTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if text:
            self.parts.append(text)

    def as_text(self) -> str:
        return "\n".join(self.parts)


class EmailGiftExtractionService:
    """Reusable email parsing and OpenAI-backed extraction pipeline."""

    _EMAIL_RE = re.compile(r"\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b", re.IGNORECASE)

    def __init__(self) -> None:
        self.extractor = OpenAIEmailExtractionService()

    def build_fetch_items(
        self,
        *,
        source: SourceConfig,
        email: ParsedEmail,
    ) -> list[RawFetchItem]:
        """Convert a parsed email plus attachments into raw items and gift extracts."""
        extraction = self.extractor.extract(email=email, source_system=source.source_system)
        if not extraction.get("is_gift_email"):
            return []

        items: list[RawFetchItem] = [
            RawFetchItem(
                object_type="email_message",
                external_object_id=email.message_id,
                payload=self._build_message_payload(email),
                event_timestamp=email.internal_date,
                content_type="application/json",
                source_channel="email",
                metadata={
                    "label_ids": email.labels,
                    "attachment_count": len(email.attachments),
                    "thread_id": email.thread_id,
                    "extraction_summary": extraction.get("extraction_summary"),
                },
            )
        ]

        attachment_object_ids: dict[str, str] = {}
        for attachment in email.attachments:
            attachment_object_id = self._attachment_external_id(email.message_id, attachment)
            attachment_object_ids[attachment.attachment_id] = attachment_object_id
            items.append(
                RawFetchItem(
                    object_type="email_attachment",
                    external_object_id=attachment_object_id,
                    external_parent_id=email.message_id,
                    payload=self._build_attachment_payload(email=email, attachment=attachment),
                    event_timestamp=email.internal_date,
                    content_type="application/json",
                    source_channel="email_attachment",
                    original_filename=attachment.filename,
                    metadata={
                        "message_id": email.message_id,
                        "filename": attachment.filename,
                        "mime_type": attachment.mime_type,
                        "size": attachment.size,
                    },
                )
            )

        deduped_gifts = self._dedupe_gifts(extraction.get("gifts") or [], email.message_id)
        for index, gift in enumerate(deduped_gifts, start=1):
            if not isinstance(gift, dict):
                continue
            payload = dict(gift)
            source_attachment_id = payload.get("sourceAttachmentId")
            external_parent_id = (
                attachment_object_ids.get(str(source_attachment_id))
                if source_attachment_id
                else email.message_id
            )
            source_record_id = payload.get("sourceRecordId")
            external_object_id = (
                str(source_record_id)
                if source_record_id
                else self._gift_external_id(email.message_id, index)
            )
            payload.setdefault("sourceRecordId", external_object_id)
            payload.setdefault("giftId", external_object_id)
            payload.setdefault("sourceParentId", email.message_id)
            payload.setdefault("messageId", email.message_id)
            items.append(
                RawFetchItem(
                    object_type="gift_extract",
                    external_object_id=external_object_id,
                    external_parent_id=external_parent_id,
                    payload=payload,
                    event_timestamp=(
                        self._parse_datetime(payload.get("giftDate")) or email.internal_date
                    ),
                    content_type="application/json",
                    source_channel="email_extraction",
                    original_filename=payload.get("sourceFilename"),
                    metadata={
                        "message_id": email.message_id,
                        "source_medium": payload.get("sourceMedium"),
                        "source_filename": payload.get("sourceFilename"),
                    },
                )
            )
        return items

    def _dedupe_gifts(self, gifts: list[Any], message_id: str) -> list[dict[str, Any]]:
        selected: dict[tuple[Any, ...], dict[str, Any]] = {}
        for candidate in gifts:
            if not isinstance(candidate, dict):
                continue
            payload = dict(candidate)
            payload.setdefault("messageId", message_id)
            dedupe_key = (
                payload.get("messageId"),
                payload.get("primaryEmail") or payload.get("donorEmail"),
                payload.get("amount"),
                payload.get("currency"),
                payload.get("recordDate") or payload.get("giftDate"),
                payload.get("campaignId") or payload.get("campaignName"),
                payload.get("receiptNumber"),
            )
            existing = selected.get(dedupe_key)
            if existing is None or self._gift_priority(payload) > self._gift_priority(existing):
                selected[dedupe_key] = payload
        return list(selected.values())

    def _gift_priority(self, payload: dict[str, Any]) -> tuple[int, int]:
        source_medium = str(payload.get("sourceMedium") or "").lower()
        has_attachment = 1 if payload.get("sourceAttachmentId") or payload.get("sourceFilename") else 0
        attachment_hint = 1 if "attachment" in source_medium or source_medium in {"pdf", "csv", "xlsx", "xls", "tsv", "txt"} else 0
        confidence = self._to_priority_number(payload.get("confidenceScore"))
        return (has_attachment + attachment_hint, confidence)

    def _to_priority_number(self, value: Any) -> int:
        try:
            return int(float(value or 0) * 1000)
        except (TypeError, ValueError):
            return 0

    def parse_gmail_message(
        self,
        payload: dict[str, Any],
        attachment_lookup: dict[str, bytes],
        *,
        body_preference: str = "plain_text",
    ) -> ParsedEmail:
        """Normalize a Gmail API message payload into reusable email fields."""
        body_text_parts: list[str] = []
        body_html_parts: list[str] = []
        attachments: list[ParsedAttachment] = []
        gmail_payload = payload.get("payload") if isinstance(payload.get("payload"), dict) else {}

        def walk(part: dict[str, Any]) -> None:
            mime_type = str(part.get("mimeType") or "")
            body = part.get("body") if isinstance(part.get("body"), dict) else {}
            filename = str(part.get("filename") or "")
            attachment_id = body.get("attachmentId")
            inline_data = body.get("data")
            if mime_type == "text/plain":
                text = self._decode_base64url(inline_data)
                if text:
                    body_text_parts.append(text.decode("utf-8", errors="replace"))
            elif mime_type == "text/html":
                html = self._decode_base64url(inline_data)
                if html:
                    body_html_parts.append(html.decode("utf-8", errors="replace"))
            elif filename and attachment_id:
                attachments.append(
                    ParsedAttachment(
                        attachment_id=str(attachment_id),
                        part_id=str(part.get("partId")) if part.get("partId") else None,
                        filename=filename,
                        mime_type=mime_type or "application/octet-stream",
                        size=body.get("size"),
                        data=attachment_lookup.get(str(attachment_id), b""),
                    )
                )
            for child in part.get("parts") or []:
                if isinstance(child, dict):
                    walk(child)

        if gmail_payload:
            walk(gmail_payload)

        headers = {
            str(item.get("name") or "").lower(): str(item.get("value") or "")
            for item in gmail_payload.get("headers") or []
            if isinstance(item, dict)
        }
        subject = headers.get("subject") or None
        from_name, from_email = self._parse_mailbox(headers.get("from"))
        _, to_email = self._parse_mailbox(headers.get("to"))
        body_text = "\n".join(part for part in body_text_parts if part).strip() or None
        body_html = "\n".join(part for part in body_html_parts if part).strip() or None
        if body_preference == "html_then_text" and body_html and not body_text:
            body_text = self._html_to_text(body_html)

        return ParsedEmail(
            message_id=str(payload.get("id")),
            thread_id=str(payload.get("threadId")) if payload.get("threadId") else None,
            history_id=str(payload.get("historyId")) if payload.get("historyId") else None,
            internal_date=self._parse_epoch_ms(payload.get("internalDate")),
            subject=subject,
            from_email=from_email,
            from_name=from_name,
            to_email=to_email,
            labels=[str(item) for item in payload.get("labelIds") or []],
            snippet=str(payload.get("snippet") or "") or None,
            body_text=body_text,
            body_html=body_html,
            attachments=attachments,
            raw_payload=payload,
        )

    def _build_message_payload(self, email: ParsedEmail) -> dict[str, Any]:
        return {
            "messageId": email.message_id,
            "threadId": email.thread_id,
            "historyId": email.history_id,
            "internalDate": email.internal_date.isoformat() if email.internal_date else None,
            "subject": email.subject,
            "fromEmail": email.from_email,
            "fromName": email.from_name,
            "toEmail": email.to_email,
            "labelIds": email.labels,
            "snippet": email.snippet,
            "bodyText": email.body_text,
            "bodyHtml": email.body_html,
            "attachments": [
                {
                    "attachmentId": item.attachment_id,
                    "filename": item.filename,
                    "mimeType": item.mime_type,
                    "size": item.size,
                }
                for item in email.attachments
            ],
        }

    def _build_attachment_payload(
        self,
        *,
        email: ParsedEmail,
        attachment: ParsedAttachment,
    ) -> dict[str, Any]:
        return {
            "messageId": email.message_id,
            "subject": email.subject,
            "attachmentId": attachment.attachment_id,
            "filename": attachment.filename,
            "mimeType": attachment.mime_type,
            "size": attachment.size,
            "contentBase64": base64.b64encode(attachment.data).decode("ascii"),
        }

    def _attachment_external_id(self, message_id: str, attachment: ParsedAttachment) -> str:
        seed = f"{message_id}|{attachment.attachment_id}|{attachment.filename}"
        return hashlib.sha1(seed.encode("utf-8")).hexdigest()[:24]

    def _gift_external_id(self, message_id: str, index: int) -> str:
        seed = f"{message_id}|gift|{index}"
        return hashlib.sha1(seed.encode("utf-8")).hexdigest()[:24]

    def _parse_datetime(self, value: Any) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.astimezone(UTC) if value.tzinfo else value.replace(tzinfo=UTC)
        text = str(value).strip()
        if not text:
            return None
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
            return parsed.astimezone(UTC) if parsed.tzinfo else parsed.replace(tzinfo=UTC)
        except ValueError:
            return None

    def _parse_epoch_ms(self, value: Any) -> datetime | None:
        if value in (None, ""):
            return None
        try:
            return datetime.fromtimestamp(int(str(value)) / 1000, tz=UTC)
        except (TypeError, ValueError):
            return None

    def _parse_mailbox(self, value: str | None) -> tuple[str | None, str | None]:
        if not value:
            return None, None
        match = re.match(r"\s*(.*?)\s*<([^>]+)>", value)
        if match:
            return match.group(1).strip('" ') or None, match.group(2).strip().lower()
        if self._EMAIL_RE.fullmatch(value.strip()):
            return None, value.strip().lower()
        return value.strip(), None

    def _html_to_text(self, value: str) -> str:
        parser = _HtmlToTextParser()
        parser.feed(value)
        return parser.as_text()

    def _decode_base64url(self, value: Any) -> bytes:
        if not isinstance(value, str) or not value:
            return b""
        padding = "=" * (-len(value) % 4)
        return base64.urlsafe_b64decode(value + padding)
