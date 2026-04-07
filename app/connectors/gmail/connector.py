"""Gmail connector for email-driven gift ingestion."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.connectors.base.connector import BaseConnector
from app.connectors.base.types import FetchRequest, FetchResult
from app.connectors.gmail.client import GmailAPIClient
from app.connectors.gmail.schemas import GmailConfig
from app.models.source_config import SourceConfig
from app.services.email_ingestion_pipeline import EmailGiftExtractionService


class GmailConnector(BaseConnector):
    """Gmail polling connector that emits raw emails, attachments, and extracted gifts."""

    source_system = "gmail"
    acquisition_mode = "email"

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self.typed_config = GmailConfig.model_validate(config)
        self.client = GmailAPIClient(self.typed_config)
        self.pipeline = EmailGiftExtractionService()

    def validate_config(self) -> None:
        self.typed_config = GmailConfig.model_validate(self.config)
        self.client = GmailAPIClient(self.typed_config)

    def test_connection(self) -> dict[str, Any]:
        profile = self.client.get_profile()
        return {
            "ok": True,
            "email_address": profile.get("emailAddress"),
            "messages_total": profile.get("messagesTotal"),
            "threads_total": profile.get("threadsTotal"),
            "history_id": profile.get("historyId"),
        }

    def list_supported_objects(self) -> list[str]:
        return ["email_message", "email_attachment", "gift_extract"]

    def runtime_config_updates(self) -> dict[str, Any] | None:
        token = self.client.current_access_token()
        if not token:
            return None
        return {"access_token": token}

    def fetch(self, request: FetchRequest) -> FetchResult:
        object_types = request.object_types or self.typed_config.enabled_object_types
        previous_cursor = (request.cursor_state or {}).get("gmail") or {}
        previous_internal_date_ms = self._parse_int(previous_cursor.get("last_internal_date_ms"))
        start_internal_date_ms = self._resolve_start_internal_date_ms(
            request.start_time,
            previous_internal_date_ms,
        )
        end_internal_date_ms = self._datetime_to_epoch_ms(request.end_time)
        page_token: str | None = None
        effective_max_messages = self.typed_config.max_messages_per_sync
        total_seen = 0
        latest_internal_date_ms = previous_internal_date_ms
        items = []
        reached_existing_history = False

        while total_seen < effective_max_messages and not reached_existing_history:
            remaining = effective_max_messages - total_seen
            payload = self.client.list_messages(
                page_token=page_token,
                max_results=min(self.typed_config.page_size, remaining),
            )
            messages = payload.get("messages")
            if not isinstance(messages, list) or not messages:
                break
            for message_ref in messages:
                if not isinstance(message_ref, dict) or not message_ref.get("id"):
                    continue
                message = self.client.get_message(str(message_ref["id"]), format_="full")
                internal_date_ms = self._parse_int(message.get("internalDate"))
                if start_internal_date_ms is not None and internal_date_ms is not None:
                    if internal_date_ms <= start_internal_date_ms:
                        reached_existing_history = True
                        break
                if end_internal_date_ms is not None and internal_date_ms is not None:
                    if internal_date_ms > end_internal_date_ms:
                        continue
                attachment_bytes = self._load_attachments(message)
                parsed_email = self.pipeline.parse_gmail_message(
                    message,
                    attachment_bytes,
                    body_preference=self.typed_config.body_preference,
                )
                fetch_items = self.pipeline.build_fetch_items(
                    source=self._pseudo_source(),
                    email=parsed_email,
                )
                items.extend(
                    item
                    for item in fetch_items
                    if item.object_type in object_types or item.object_type == "gift_extract"
                )
                total_seen += 1
                if internal_date_ms is not None:
                    latest_internal_date_ms = max(
                        latest_internal_date_ms or internal_date_ms,
                        internal_date_ms,
                    )
                if total_seen >= effective_max_messages:
                    break
            page_token = payload.get("nextPageToken")
            if not page_token:
                break

        cursor_state = {
            "gmail": {
                "last_internal_date_ms": latest_internal_date_ms,
                "last_synced_at": datetime.now(tz=UTC).isoformat(),
            }
        }
        return FetchResult(
            items=items,
            cursor_state=cursor_state,
            metadata={
                "fetched_object_types": object_types,
                "messages_processed": total_seen,
                "processing_scope": "incremental_since_last_fetch",
                "start_internal_date_ms": start_internal_date_ms,
                "end_internal_date_ms": end_internal_date_ms,
            },
        )

    def normalize_raw_metadata(self, payload: dict[str, Any] | list[Any] | str) -> dict[str, Any]:
        if isinstance(payload, dict):
            return {"top_level_keys": sorted(payload.keys())}
        if isinstance(payload, list):
            return {"item_count": len(payload)}
        return {"preview": str(payload)[:200]}

    def extract_external_ids(
        self,
        payload: dict[str, Any] | list[Any] | str,
    ) -> dict[str, str | None]:
        if not isinstance(payload, dict):
            return {"external_object_id": None, "external_parent_id": None}
        return {
            "external_object_id": payload.get("messageId") or payload.get("giftRecordId"),
            "external_parent_id": (
                payload.get("sourceAttachmentObjectId") or payload.get("threadId")
            ),
        }

    def _load_attachments(self, message: dict[str, Any]) -> dict[str, bytes]:
        if not self.typed_config.process_attachments:
            return {}
        attachment_lookup: dict[str, bytes] = {}

        def walk(part: dict[str, Any]) -> None:
            body = part.get("body") if isinstance(part.get("body"), dict) else {}
            attachment_id = body.get("attachmentId")
            filename = str(part.get("filename") or "")
            if attachment_id and filename:
                extension = self._extension(filename)
                if extension in self.typed_config.attachment_extensions:
                    payload = self.client.get_attachment(str(message["id"]), str(attachment_id))
                    raw = self.pipeline._decode_base64url(payload.get("data"))
                    if raw and len(raw) <= self.typed_config.max_attachment_bytes:
                        attachment_lookup[str(attachment_id)] = raw
            for child in part.get("parts") or []:
                if isinstance(child, dict):
                    walk(child)

        payload = message.get("payload")
        if isinstance(payload, dict):
            walk(payload)
        return attachment_lookup

    def _extension(self, filename: str) -> str:
        lowered = filename.lower()
        if "." not in lowered:
            return ""
        return lowered[lowered.rfind(".") :]

    def _pseudo_source(self) -> SourceConfig:
        return SourceConfig(
            source_name="gmail",
            source_system=self.source_system,
            acquisition_mode=self.acquisition_mode,
            auth_type="oauth",
            enabled=True,
            schedule=None,
            config_json={"gift_keywords": self.typed_config.gift_keywords},
            parser_name=None,
            dedupe_keys=None,
            notes=None,
        )

    def _parse_int(self, value: Any) -> int | None:
        if value in (None, ""):
            return None
        try:
            return int(str(value))
        except (TypeError, ValueError):
            return None

    def _resolve_start_internal_date_ms(
        self,
        requested_start: datetime | None,
        previous_internal_date_ms: int | None,
    ) -> int | None:
        requested_start_ms = self._datetime_to_epoch_ms(requested_start)
        if requested_start_ms is None:
            return previous_internal_date_ms
        if previous_internal_date_ms is None:
            return requested_start_ms
        return max(requested_start_ms, previous_internal_date_ms)

    def _datetime_to_epoch_ms(self, value: datetime | None) -> int | None:
        if value is None:
            return None
        return int(value.astimezone(UTC).timestamp() * 1000)
