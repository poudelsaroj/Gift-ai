"""Add canonical normalized record fields to staging gifts."""

from alembic import op
import sqlalchemy as sa

revision = "20260401_0004"
down_revision = "20260401_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("staging_gifts", sa.Column("record_type", sa.String(length=50), nullable=True))
    op.add_column("staging_gifts", sa.Column("source_record_id", sa.String(length=255), nullable=True))
    op.add_column("staging_gifts", sa.Column("source_parent_id", sa.String(length=255), nullable=True))
    op.add_column("staging_gifts", sa.Column("primary_name", sa.String(length=255), nullable=True))
    op.add_column("staging_gifts", sa.Column("primary_email", sa.String(length=255), nullable=True))
    op.add_column("staging_gifts", sa.Column("record_date", sa.Date(), nullable=True))
    op.add_column("staging_gifts", sa.Column("campaign_id", sa.String(length=255), nullable=True))
    op.add_column("staging_gifts", sa.Column("campaign_name", sa.String(length=255), nullable=True))
    op.add_column("staging_gifts", sa.Column("related_entity_id", sa.String(length=255), nullable=True))
    op.add_column("staging_gifts", sa.Column("related_entity_name", sa.String(length=255), nullable=True))
    op.add_column("staging_gifts", sa.Column("extra_metadata", sa.JSON(), nullable=True))

    op.create_index("ix_staging_gifts_record_type", "staging_gifts", ["record_type"], unique=False)
    op.create_index("ix_staging_gifts_source_record_id", "staging_gifts", ["source_record_id"], unique=False)

    op.execute(
        """
        UPDATE staging_gifts
        SET
          record_type = COALESCE(record_type, 'gift'),
          source_record_id = COALESCE(source_record_id, gift_id),
          source_parent_id = COALESCE(source_parent_id, participant_id),
          primary_name = COALESCE(primary_name, donor_name, participant_name),
          primary_email = COALESCE(primary_email, donor_email),
          record_date = COALESCE(record_date, gift_date),
          campaign_id = COALESCE(campaign_id, challenge_id),
          campaign_name = COALESCE(campaign_name, challenge_name),
          related_entity_id = COALESCE(related_entity_id, participant_id),
          related_entity_name = COALESCE(related_entity_name, participant_name)
        """
    )


def downgrade() -> None:
    op.drop_index("ix_staging_gifts_source_record_id", table_name="staging_gifts")
    op.drop_index("ix_staging_gifts_record_type", table_name="staging_gifts")
    op.drop_column("staging_gifts", "extra_metadata")
    op.drop_column("staging_gifts", "related_entity_name")
    op.drop_column("staging_gifts", "related_entity_id")
    op.drop_column("staging_gifts", "campaign_name")
    op.drop_column("staging_gifts", "campaign_id")
    op.drop_column("staging_gifts", "record_date")
    op.drop_column("staging_gifts", "primary_email")
    op.drop_column("staging_gifts", "primary_name")
    op.drop_column("staging_gifts", "source_parent_id")
    op.drop_column("staging_gifts", "source_record_id")
    op.drop_column("staging_gifts", "record_type")
