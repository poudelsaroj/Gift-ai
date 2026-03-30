"""Lightweight job runner abstraction."""

from sqlalchemy.orm import Session

from app.models.ingestion_run import IngestionRun
from app.models.source_config import SourceConfig
from app.services.ingestion_service import IngestionService


class JobRunner:
    """Synchronous worker abstraction, replaceable with a queue later."""

    def __init__(self) -> None:
        self.ingestion_service = IngestionService()

    def run_ingestion(
        self,
        db: Session,
        source: SourceConfig,
        *,
        run_type: str,
        trigger_type: str,
        object_types: list[str] | None = None,
    ) -> IngestionRun:
        """Execute a source ingestion job immediately."""
        return self.ingestion_service.execute(
            db,
            source,
            run_type=run_type,
            trigger_type=trigger_type,
            object_types=object_types,
        )

