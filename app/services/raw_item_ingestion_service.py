"""Raw item persistence for ingestion workflows."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.connectors.base.types import RawFetchItem
from app.core.config import get_settings
from app.dedupe.service import DedupeService
from app.models.raw_object import RawObject
from app.models.source_config import SourceConfig
from app.services.normalization_service import NormalizationService
from app.services.raw_object_service import RawObjectService
from app.storage.filesystem import FilesystemStorage


@dataclass(slots=True)
class PersistedRawItems:
    """Summary of raw items persisted for a run."""

    raw_objects: list[RawObject]
    duplicates_detected_count: int


class RawItemIngestionService:
    """Persist connector-emitted raw items and derived metadata."""

    def __init__(
        self,
        storage: FilesystemStorage | None = None,
        raw_object_service: RawObjectService | None = None,
        dedupe_service: DedupeService | None = None,
        normalization_service: NormalizationService | None = None,
    ) -> None:
        settings = get_settings()
        self.storage = storage or FilesystemStorage(settings.raw_storage_root)
        self.raw_object_service = raw_object_service or RawObjectService()
        self.dedupe_service = dedupe_service or DedupeService()
        self.normalization_service = normalization_service or NormalizationService()

    def persist_items(
        self,
        db: Session,
        source: SourceConfig,
        run_id: int,
        items: list[RawFetchItem],
    ) -> PersistedRawItems:
        """Persist connector-emitted items for a single ingestion run."""
        raw_objects: list[RawObject] = []
        duplicates = 0
        for item in items:
            fetched_at = datetime.now(tz=UTC)
            storage_path = self.storage.save_json_payload(
                source_system=source.source_system,
                run_id=run_id,
                object_type=item.object_type,
                object_id=item.external_object_id,
                payload=item.payload if isinstance(item.payload, (dict, list)) else {"raw": item.payload},
                fetched_at=fetched_at,
            )
            raw_object = self.raw_object_service.create(
                db,
                source_id=source.id,
                ingestion_run_id=run_id,
                source_channel=item.source_channel,
                source_system=source.source_system,
                external_object_type=item.object_type,
                external_object_id=item.external_object_id,
                external_parent_id=item.external_parent_id,
                event_timestamp=item.event_timestamp,
                original_filename=item.original_filename,
                content_type=item.content_type,
                payload_storage_path=storage_path,
                raw_payload_ref=storage_path,
                metadata_json=item.metadata,
                payload=item.payload,
            )
            db.flush()
            decision = self.dedupe_service.detect(db, raw_object)
            raw_object.duplicate_status = decision.status
            raw_object.duplicate_of_id = decision.duplicate_of_id
            raw_object.dedupe_reason = decision.reason
            if decision.status != "unique":
                duplicates += 1
            db.add(raw_object)
            if isinstance(item.payload, dict):
                self.normalization_service.normalize_raw_object(db, raw_object, item.payload)
            raw_objects.append(raw_object)
        return PersistedRawItems(
            raw_objects=raw_objects,
            duplicates_detected_count=duplicates,
        )
