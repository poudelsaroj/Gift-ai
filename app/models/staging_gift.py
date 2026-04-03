"""Canonical normalized record model for cross-source intake."""

from datetime import date
from decimal import Decimal

from sqlalchemy import JSON, Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class StagingGift(TimestampMixin, Base):
    """Canonical normalized record table used across source systems."""

    __tablename__ = "staging_gifts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    raw_object_id: Mapped[int] = mapped_column(ForeignKey("raw_objects.id"), nullable=False, index=True)
    record_type: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    source_record_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    source_parent_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    gift_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_channel: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_system: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    primary_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    primary_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    donor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    donor_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    record_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    gift_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    payment_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    gift_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    campaign_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    campaign_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    challenge_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    challenge_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    related_entity_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    related_entity_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    participant_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    participant_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    team_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    team_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    charity_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    receipt_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    memo: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_payload_ref: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    duplicate_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    extra_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
