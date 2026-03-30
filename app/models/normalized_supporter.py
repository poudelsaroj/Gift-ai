"""Normalized supporter read model."""

from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class NormalizedSupporter(TimestampMixin, Base):
    """Lightweight normalized supporter record for UI and reporting."""

    __tablename__ = "normalized_supporters"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    raw_object_id: Mapped[int] = mapped_column(ForeignKey("raw_objects.id"), nullable=False, index=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("source_configs.id"), nullable=False, index=True)
    supporter_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    user_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    supporter_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    team_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    team_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    donation_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    donation_count: Mapped[int | None] = mapped_column(nullable=True)
    team_credit_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    team_credit_count: Mapped[int | None] = mapped_column(nullable=True)
    total_points_earned: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    event_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    event_ids: Mapped[str | None] = mapped_column(String(500), nullable=True)
    accepted: Mapped[str | None] = mapped_column(String(50), nullable=True)

