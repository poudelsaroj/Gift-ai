"""Raw object model."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class RawObject(TimestampMixin, Base):
    """Stores fetched raw payload metadata and lineage."""

    __tablename__ = "raw_objects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("source_configs.id"), nullable=False, index=True)
    ingestion_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("ingestion_runs.id"),
        nullable=True,
        index=True,
    )
    source_channel: Mapped[str] = mapped_column(String(50), nullable=False)
    source_system: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    external_object_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    external_object_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    external_parent_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    event_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    payload_storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    raw_payload_ref: Mapped[str | None] = mapped_column(String(500), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    parse_status: Mapped[str] = mapped_column(String(50), default="not_parsed", nullable=False)
    duplicate_status: Mapped[str] = mapped_column(String(50), default="unique", nullable=False)
    duplicate_of_id: Mapped[int | None] = mapped_column(ForeignKey("raw_objects.id"), nullable=True)
    dedupe_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    source = relationship("SourceConfig", back_populates="raw_objects")
    ingestion_run = relationship("IngestionRun", back_populates="raw_objects")
    duplicate_of = relationship("RawObject", remote_side=[id])

