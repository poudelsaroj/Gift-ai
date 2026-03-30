"""Raw object service."""

import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.raw_object import RawObject


class RawObjectService:
    """Persistence helpers for raw objects."""

    def compute_checksum(self, payload: dict[str, Any] | list[Any] | str) -> str:
        """Compute a stable sha256 checksum."""
        if isinstance(payload, str):
            body = payload.encode("utf-8")
        else:
            body = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(body).hexdigest()

    def create(
        self,
        db: Session,
        *,
        source_id: int,
        ingestion_run_id: int,
        source_channel: str,
        source_system: str,
        external_object_type: str,
        external_object_id: str | None,
        external_parent_id: str | None,
        event_timestamp: datetime | None,
        original_filename: str | None,
        content_type: str,
        payload_storage_path: str,
        raw_payload_ref: str | None,
        metadata_json: dict[str, Any] | None,
        payload: dict[str, Any] | list[Any] | str,
    ) -> RawObject:
        raw_object = RawObject(
            source_id=source_id,
            ingestion_run_id=ingestion_run_id,
            source_channel=source_channel,
            source_system=source_system,
            external_object_type=external_object_type,
            external_object_id=external_object_id,
            external_parent_id=external_parent_id,
            fetched_at=datetime.now(tz=UTC),
            event_timestamp=event_timestamp,
            original_filename=original_filename,
            content_type=content_type,
            checksum_sha256=self.compute_checksum(payload),
            payload_storage_path=payload_storage_path,
            raw_payload_ref=raw_payload_ref,
            metadata_json=metadata_json,
            parse_status="metadata_extracted",
        )
        db.add(raw_object)
        db.flush()
        return raw_object

    def list(self, db: Session, offset: int = 0, limit: int = 100) -> tuple[list[RawObject], int]:
        items = list(db.scalars(select(RawObject).offset(offset).limit(limit)))
        total = db.scalar(select(func.count()).select_from(RawObject)) or 0
        return items, total

    def get(self, db: Session, raw_object_id: int) -> RawObject | None:
        return db.get(RawObject, raw_object_id)

