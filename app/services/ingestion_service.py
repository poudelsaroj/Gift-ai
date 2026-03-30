"""Ingestion execution service."""

from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.connectors.registry import ConnectorRegistry
from app.connectors.base.types import FetchRequest
from app.core.config import get_settings
from app.dedupe.service import DedupeService
from app.models.ingestion_run import IngestionRun
from app.models.source_config import SourceConfig
from app.storage.filesystem import FilesystemStorage
from app.utils.security import redact_config
from app.services.normalization_service import NormalizationService
from app.services.raw_object_service import RawObjectService

logger = structlog.get_logger(__name__)


class IngestionService:
    """Coordinates connector execution, raw storage, and run tracking."""

    def __init__(self) -> None:
        settings = get_settings()
        self.storage = FilesystemStorage(settings.raw_storage_root)
        self.raw_object_service = RawObjectService()
        self.dedupe_service = DedupeService()
        self.normalization_service = NormalizationService()

    def create_run(self, db: Session, source_id: int, run_type: str, trigger_type: str) -> IngestionRun:
        """Create a pending ingestion run."""
        run = IngestionRun(
            source_id=source_id,
            run_type=run_type,
            trigger_type=trigger_type,
            status="pending",
            metadata_json={},
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        return run

    def execute(
        self,
        db: Session,
        source: SourceConfig,
        *,
        run_type: str,
        trigger_type: str,
        object_types: list[str] | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> IngestionRun:
        """Execute an ingestion run synchronously."""
        connector = ConnectorRegistry.get_connector(source.source_system, source.config_json)
        connector.validate_config()

        run = self.create_run(db, source.id, run_type, trigger_type)
        run.status = "running"
        run.started_at = datetime.now(tz=UTC)
        db.add(run)
        db.commit()
        db.refresh(run)

        logger.info(
            "ingestion_run_started",
            source_id=source.id,
            ingestion_run_id=run.id,
            source_system=source.source_system,
            config=redact_config(source.config_json),
        )

        previous_cursor = self._latest_cursor(db, source.id)
        request = FetchRequest(
            run_type=run_type,
            trigger_type=trigger_type,
            object_types=object_types,
            cursor_state=previous_cursor,
            start_time=start_time,
            end_time=end_time,
        )

        try:
            result = connector.fetch_incremental(request)
            duplicates = 0
            for item in result.items:
                fetched_at = datetime.now(tz=UTC)
                storage_path = self.storage.save_json_payload(
                    source_system=source.source_system,
                    run_id=run.id,
                    object_type=item.object_type,
                    object_id=item.external_object_id,
                    payload=item.payload if isinstance(item.payload, (dict, list)) else {"raw": item.payload},
                    fetched_at=fetched_at,
                )
                raw_object = self.raw_object_service.create(
                    db,
                    source_id=source.id,
                    ingestion_run_id=run.id,
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
            run.status = "completed"
            run.completed_at = datetime.now(tz=UTC)
            run.records_fetched_count = len(result.items)
            run.duplicates_detected_count = duplicates
            run.cursor_state = result.cursor_state
            run.metadata_json = result.metadata
            db.add(run)
            db.commit()
            db.refresh(run)
            logger.info(
                "ingestion_run_completed",
                source_id=source.id,
                ingestion_run_id=run.id,
                records_fetched_count=run.records_fetched_count,
                duplicates_detected_count=run.duplicates_detected_count,
            )
            return run
        except Exception as exc:
            run.status = "failed"
            run.completed_at = datetime.now(tz=UTC)
            run.error_message = str(exc)
            db.add(run)
            db.commit()
            logger.exception(
                "ingestion_run_failed",
                source_id=source.id,
                ingestion_run_id=run.id,
                error_message=str(exc),
            )
            raise

    def list_runs(self, db: Session, offset: int = 0, limit: int = 100) -> tuple[list[IngestionRun], int]:
        """List ingestion runs."""
        items = list(db.scalars(select(IngestionRun).offset(offset).limit(limit)))
        total = db.scalar(select(func.count()).select_from(IngestionRun)) or 0
        return items, total

    def get_run(self, db: Session, run_id: int) -> IngestionRun | None:
        """Return an ingestion run by id."""
        return db.get(IngestionRun, run_id)

    def list_runs_for_source(
        self,
        db: Session,
        source_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[list[IngestionRun], int]:
        """List runs for a source."""
        items = list(
            db.scalars(
                select(IngestionRun).where(IngestionRun.source_id == source_id).offset(offset).limit(limit)
            )
        )
        total = db.scalar(
            select(func.count()).select_from(IngestionRun).where(IngestionRun.source_id == source_id)
        ) or 0
        return items, total

    def _latest_cursor(self, db: Session, source_id: int) -> dict[str, Any] | None:
        latest_run = db.scalar(
            select(IngestionRun)
            .where(IngestionRun.source_id == source_id, IngestionRun.cursor_state.is_not(None))
            .order_by(IngestionRun.id.desc())
            .limit(1)
        )
        return latest_run.cursor_state if latest_run else None
