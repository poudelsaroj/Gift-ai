"""Ingestion execution service."""

from __future__ import annotations

from typing import Any

import structlog
from sqlalchemy.orm import Session

from app.connectors.base.types import FetchRequest, RawFetchItem
from app.connectors.registry import ConnectorRegistry
from app.models.ingestion_run import IngestionRun
from app.models.raw_object import RawObject
from app.models.source_config import SourceConfig
from app.services.ingestion_run_service import IngestionRunService
from app.services.raw_item_ingestion_service import RawItemIngestionService
from app.utils.security import redact_config

logger = structlog.get_logger(__name__)


class IngestionService:
    """Coordinate connector execution, run lifecycle, and raw-item persistence."""

    def __init__(
        self,
        *,
        connector_registry: Any = ConnectorRegistry,
        ingestion_run_service: IngestionRunService | None = None,
        raw_item_ingestion_service: RawItemIngestionService | None = None,
    ) -> None:
        self.connector_registry = connector_registry
        self.ingestion_run_service = ingestion_run_service or IngestionRunService()
        self.raw_item_ingestion_service = raw_item_ingestion_service or RawItemIngestionService()

    def create_run(self, db: Session, source_id: int, run_type: str, trigger_type: str) -> IngestionRun:
        """Create a pending ingestion run."""
        return self.ingestion_run_service.create_pending_run(db, source_id, run_type, trigger_type)

    def execute(
        self,
        db: Session,
        source: SourceConfig,
        *,
        run_type: str,
        trigger_type: str,
        object_types: list[str] | None = None,
        start_time: Any = None,
        end_time: Any = None,
    ) -> IngestionRun:
        """Execute an ingestion run synchronously."""
        connector = self._create_connector(source)
        connector.validate_config()

        run = self.ingestion_run_service.create_pending_run(db, source.id, run_type, trigger_type)
        run = self.ingestion_run_service.mark_running(db, run)

        logger.info(
            "ingestion_run_started",
            source_id=source.id,
            ingestion_run_id=run.id,
            source_system=source.source_system,
            config=redact_config(source.config_json),
        )

        previous_cursor = self.ingestion_run_service.latest_cursor(db, source.id)
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
            self._persist_connector_config_updates(db, source, connector)
            persisted = self.raw_item_ingestion_service.persist_items(db, source, run.id, result.items)
            run = self.ingestion_run_service.mark_completed(
                db,
                run,
                records_fetched_count=len(persisted.raw_objects),
                duplicates_detected_count=persisted.duplicates_detected_count,
                cursor_state=result.cursor_state,
                metadata_json=result.metadata,
            )
            logger.info(
                "ingestion_run_completed",
                source_id=source.id,
                ingestion_run_id=run.id,
                records_fetched_count=run.records_fetched_count,
                duplicates_detected_count=run.duplicates_detected_count,
            )
            return run
        except Exception as exc:
            run = self.ingestion_run_service.mark_failed(db, run, str(exc))
            logger.exception(
                "ingestion_run_failed",
                source_id=source.id,
                ingestion_run_id=run.id,
                error_message=str(exc),
            )
            raise

    def ingest_webhook_payload(
        self,
        db: Session,
        source: SourceConfig,
        *,
        object_type: str,
        payload: dict[str, Any] | list[Any] | str,
        external_object_id: str | None = None,
        external_parent_id: str | None = None,
        event_timestamp: Any = None,
        content_type: str = "application/json",
        source_channel: str = "webhook",
        original_filename: str | None = None,
        metadata_json: dict[str, Any] | None = None,
    ) -> tuple[IngestionRun, RawObject]:
        """Persist a single webhook payload as an ingestion run and raw object."""
        run = self.ingestion_run_service.create_pending_run(
            db,
            source.id,
            run_type="incremental",
            trigger_type="webhook",
        )
        run = self.ingestion_run_service.mark_running(db, run)

        try:
            persisted = self.raw_item_ingestion_service.persist_items(
                db,
                source,
                run.id,
                [
                    RawFetchItem(
                        object_type=object_type,
                        external_object_id=external_object_id,
                        external_parent_id=external_parent_id,
                        payload=payload,
                        event_timestamp=event_timestamp,
                        content_type=content_type,
                        source_channel=source_channel,
                        original_filename=original_filename,
                        metadata=metadata_json or {},
                    )
                ],
            )
            run = self.ingestion_run_service.mark_completed(
                db,
                run,
                records_fetched_count=len(persisted.raw_objects),
                duplicates_detected_count=persisted.duplicates_detected_count,
                metadata_json={"webhook_object_type": object_type},
            )
            return run, persisted.raw_objects[0]
        except Exception as exc:
            run = self.ingestion_run_service.mark_failed(db, run, str(exc))
            logger.exception(
                "ingestion_run_failed",
                source_id=source.id,
                ingestion_run_id=run.id,
                error_message=str(exc),
            )
            raise

    def ingest_items(
        self,
        db: Session,
        source: SourceConfig,
        *,
        items: list[RawFetchItem],
        run_type: str = "full",
        trigger_type: str = "manual_upload",
        metadata_json: dict[str, Any] | None = None,
    ) -> IngestionRun:
        """Persist a prepared batch of raw items as a single ingestion run."""
        run = self.ingestion_run_service.create_pending_run(db, source.id, run_type, trigger_type)
        run = self.ingestion_run_service.mark_running(db, run)

        try:
            persisted = self.raw_item_ingestion_service.persist_items(db, source, run.id, items)
            return self.ingestion_run_service.mark_completed(
                db,
                run,
                records_fetched_count=len(persisted.raw_objects),
                duplicates_detected_count=persisted.duplicates_detected_count,
                metadata_json=metadata_json or {},
            )
        except Exception as exc:
            run = self.ingestion_run_service.mark_failed(db, run, str(exc))
            logger.exception(
                "ingestion_run_failed",
                source_id=source.id,
                ingestion_run_id=run.id,
                error_message=str(exc),
            )
            raise

    def list_runs(self, db: Session, offset: int = 0, limit: int = 100) -> tuple[list[IngestionRun], int]:
        """List ingestion runs."""
        return self.ingestion_run_service.list_runs(db, offset=offset, limit=limit)

    def get_run(self, db: Session, run_id: int) -> IngestionRun | None:
        """Return an ingestion run by id."""
        return self.ingestion_run_service.get_run(db, run_id)

    def list_runs_for_source(
        self,
        db: Session,
        source_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[list[IngestionRun], int]:
        """List runs for a source."""
        return self.ingestion_run_service.list_runs_for_source(
            db,
            source_id,
            offset=offset,
            limit=limit,
        )

    def _create_connector(self, source: SourceConfig) -> Any:
        factory = getattr(self.connector_registry, "create_connector", None)
        if callable(factory):
            return factory(source.source_system, source.config_json)
        return self.connector_registry.get_connector(source.source_system, source.config_json)

    def _persist_connector_config_updates(self, db: Session, source: SourceConfig, connector: Any) -> None:
        updates = connector.runtime_config_updates()
        if not updates:
            return
        source.config_json = {**(source.config_json or {}), **updates}
        db.add(source)
        db.commit()
        db.refresh(source)
