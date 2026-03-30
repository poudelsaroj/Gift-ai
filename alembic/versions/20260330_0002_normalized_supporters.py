"""Add normalized supporters."""

from alembic import op
import sqlalchemy as sa

revision = "20260330_0002"
down_revision = "20260330_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "normalized_supporters",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("raw_object_id", sa.Integer(), sa.ForeignKey("raw_objects.id"), nullable=False),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("source_configs.id"), nullable=False),
        sa.Column("supporter_id", sa.String(length=255), nullable=True),
        sa.Column("user_id", sa.String(length=255), nullable=True),
        sa.Column("supporter_name", sa.String(length=255), nullable=True),
        sa.Column("team_id", sa.String(length=255), nullable=True),
        sa.Column("team_name", sa.String(length=255), nullable=True),
        sa.Column("donation_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("donation_count", sa.Integer(), nullable=True),
        sa.Column("team_credit_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("team_credit_count", sa.Integer(), nullable=True),
        sa.Column("total_points_earned", sa.Numeric(12, 2), nullable=True),
        sa.Column("event_id", sa.String(length=255), nullable=True),
        sa.Column("event_ids", sa.String(length=500), nullable=True),
        sa.Column("accepted", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_normalized_supporters_id", "normalized_supporters", ["id"])
    op.create_index("ix_normalized_supporters_raw_object_id", "normalized_supporters", ["raw_object_id"])
    op.create_index("ix_normalized_supporters_source_id", "normalized_supporters", ["source_id"])
    op.create_index("ix_normalized_supporters_supporter_id", "normalized_supporters", ["supporter_id"])


def downgrade() -> None:
    op.drop_index("ix_normalized_supporters_supporter_id", table_name="normalized_supporters")
    op.drop_index("ix_normalized_supporters_source_id", table_name="normalized_supporters")
    op.drop_index("ix_normalized_supporters_raw_object_id", table_name="normalized_supporters")
    op.drop_index("ix_normalized_supporters_id", table_name="normalized_supporters")
    op.drop_table("normalized_supporters")
