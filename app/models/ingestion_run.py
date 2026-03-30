"""Ingestion run model."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class IngestionRun(TimestampMixin, Base):
    """Tracks the lifecycle of a source ingestion run."""

    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("source_configs.id"), nullable=False, index=True)
    run_type: Mapped[str] = mapped_column(String(50), nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    records_fetched_count: Mapped[int] = mapped_column(default=0, nullable=False)
    files_fetched_count: Mapped[int] = mapped_column(default=0, nullable=False)
    duplicates_detected_count: Mapped[int] = mapped_column(default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    cursor_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    source = relationship("SourceConfig", back_populates="ingestion_runs")
    raw_objects = relationship("RawObject", back_populates="ingestion_run")

