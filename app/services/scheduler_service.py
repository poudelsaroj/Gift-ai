"""Simple in-process scheduler for polling sources."""

from __future__ import annotations

import threading
import time
from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.source_config import SourceConfig
from app.services.ingestion_service import IngestionService

logger = structlog.get_logger(__name__)


class SchedulerService:
    """Very small Phase 1 scheduler for polling-enabled sources."""

    def __init__(self, poll_seconds: int = 60) -> None:
        self.poll_seconds = poll_seconds
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self.ingestion_service = IngestionService()

    def start(self) -> None:
        """Start the scheduler thread once."""
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the scheduler thread."""
        self._stop.set()

    def _run_loop(self) -> None:
        while not self._stop.is_set():
            try:
                self.run_due_sources()
            except Exception:
                logger.exception("scheduler_cycle_failed")
            self._stop.wait(self.poll_seconds)

    def run_due_sources(self) -> int:
        """Execute due scheduled sources and return the number started."""
        started = 0
        with SessionLocal() as db:
            sources = list(
                db.scalars(
                    select(SourceConfig).where(SourceConfig.enabled.is_(True), SourceConfig.schedule.is_not(None))
                )
            )
            now = datetime.now(tz=UTC)
            for source in sources:
                if not self._is_due(source, now):
                    continue
                self.ingestion_service.execute(
                    db,
                    source,
                    run_type="incremental",
                    trigger_type="scheduled",
                )
                metadata = dict(source.config_json)
                metadata["_scheduler"] = {"last_run_at": now.isoformat()}
                source.config_json = metadata
                db.add(source)
                db.commit()
                started += 1
        return started

    def _is_due(self, source: SourceConfig, now: datetime) -> bool:
        schedule = (source.schedule or "").strip().lower()
        if not schedule or schedule == "manual":
            return False
        last_run = ((source.config_json or {}).get("_scheduler") or {}).get("last_run_at")
        last_dt = datetime.fromisoformat(last_run) if last_run else None
        if schedule == "daily":
            return last_dt is None or now - last_dt >= timedelta(days=1)
        if schedule == "hourly":
            return last_dt is None or now - last_dt >= timedelta(hours=1)
        if schedule == "every_6_hours":
            return last_dt is None or now - last_dt >= timedelta(hours=6)
        return False

