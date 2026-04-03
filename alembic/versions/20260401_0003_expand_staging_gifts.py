"""Expand staging gifts for normalized donor and attribution fields."""

from alembic import op
import sqlalchemy as sa

revision = "20260401_0003"
down_revision = "20260330_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("staging_gifts", sa.Column("donor_email", sa.String(length=255), nullable=True))
    op.add_column("staging_gifts", sa.Column("company_name", sa.String(length=255), nullable=True))
    op.add_column("staging_gifts", sa.Column("challenge_id", sa.String(length=255), nullable=True))
    op.add_column("staging_gifts", sa.Column("challenge_name", sa.String(length=255), nullable=True))
    op.add_column("staging_gifts", sa.Column("participant_id", sa.String(length=255), nullable=True))
    op.add_column("staging_gifts", sa.Column("participant_name", sa.String(length=255), nullable=True))
    op.add_column("staging_gifts", sa.Column("team_id", sa.String(length=255), nullable=True))
    op.add_column("staging_gifts", sa.Column("team_name", sa.String(length=255), nullable=True))
    op.add_column("staging_gifts", sa.Column("charity_id", sa.String(length=255), nullable=True))
    op.add_column("staging_gifts", sa.Column("receipt_number", sa.String(length=255), nullable=True))
    op.add_column("staging_gifts", sa.Column("duplicate_status", sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column("staging_gifts", "duplicate_status")
    op.drop_column("staging_gifts", "receipt_number")
    op.drop_column("staging_gifts", "charity_id")
    op.drop_column("staging_gifts", "team_name")
    op.drop_column("staging_gifts", "team_id")
    op.drop_column("staging_gifts", "participant_name")
    op.drop_column("staging_gifts", "participant_id")
    op.drop_column("staging_gifts", "challenge_name")
    op.drop_column("staging_gifts", "challenge_id")
    op.drop_column("staging_gifts", "company_name")
    op.drop_column("staging_gifts", "donor_email")
