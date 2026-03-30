"""Source configuration model."""

from sqlalchemy import Boolean, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class SourceConfig(TimestampMixin, Base):
    """Stored connector/source configuration."""

    __tablename__ = "source_configs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_system: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    acquisition_mode: Mapped[str] = mapped_column(String(50), nullable=False)
    auth_type: Mapped[str] = mapped_column(String(50), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    schedule: Mapped[str | None] = mapped_column(String(100), nullable=True)
    config_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    parser_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    dedupe_keys: Mapped[list | None] = mapped_column(JSON, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    ingestion_runs = relationship("IngestionRun", back_populates="source", cascade="all, delete-orphan")
    raw_objects = relationship("RawObject", back_populates="source")

