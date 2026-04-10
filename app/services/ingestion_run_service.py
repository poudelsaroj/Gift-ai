"""Ingestion run lifecycle service."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ingestion_run import IngestionRun


class IngestionRunService:
    """Manage ingestion run creation and status transitions."""

    def create_pending_run(self, db: Session, source_id: int, run_type: str, trigger_type: str) -> IngestionRun:
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

    def mark_running(self, db: Session, run: IngestionRun) -> IngestionRun:
        """Mark a run as actively executing."""
        run.status = "running"
        run.started_at = datetime.now(tz=UTC)
        return self._save(db, run)

    def mark_completed(
        self,
        db: Session,
        run: IngestionRun,
        *,
        records_fetched_count: int,
        duplicates_detected_count: int,
        cursor_state: dict[str, Any] | None = None,
        metadata_json: dict[str, Any] | None = None,
    ) -> IngestionRun:
        """Mark a run as completed and persist summary metadata."""
        run.status = "completed"
        run.completed_at = datetime.now(tz=UTC)
        run.records_fetched_count = records_fetched_count
        run.duplicates_detected_count = duplicates_detected_count
        run.cursor_state = cursor_state
        run.metadata_json = metadata_json or {}
        return self._save(db, run)

    def mark_failed(self, db: Session, run: IngestionRun, error_message: str) -> IngestionRun:
        """Mark a run as failed."""
        run.status = "failed"
        run.completed_at = datetime.now(tz=UTC)
        run.error_message = error_message
        return self._save(db, run)

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

    def latest_cursor(self, db: Session, source_id: int) -> dict[str, Any] | None:
        """Return the most recent cursor state for a source."""
        latest_run = db.scalar(
            select(IngestionRun)
            .where(IngestionRun.source_id == source_id, IngestionRun.cursor_state.is_not(None))
            .order_by(IngestionRun.id.desc())
            .limit(1)
        )
        return latest_run.cursor_state if latest_run else None

    def _save(self, db: Session, run: IngestionRun) -> IngestionRun:
        db.add(run)
        db.commit()
        db.refresh(run)
        return run
