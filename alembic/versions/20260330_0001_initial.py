"""Initial schema."""

from alembic import op
import sqlalchemy as sa

revision = "20260330_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "source_configs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_name", sa.String(length=255), nullable=False),
        sa.Column("source_system", sa.String(length=100), nullable=False),
        sa.Column("acquisition_mode", sa.String(length=50), nullable=False),
        sa.Column("auth_type", sa.String(length=50), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("schedule", sa.String(length=100), nullable=True),
        sa.Column("config_json", sa.JSON(), nullable=False),
        sa.Column("parser_name", sa.String(length=100), nullable=True),
        sa.Column("dedupe_keys", sa.JSON(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_source_configs_id", "source_configs", ["id"])
    op.create_index("ix_source_configs_source_system", "source_configs", ["source_system"])

    op.create_table(
        "ingestion_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("source_configs.id"), nullable=False),
        sa.Column("run_type", sa.String(length=50), nullable=False),
        sa.Column("trigger_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("records_fetched_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("files_fetched_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duplicates_detected_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("cursor_state", sa.JSON(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ingestion_runs_id", "ingestion_runs", ["id"])
    op.create_index("ix_ingestion_runs_source_id", "ingestion_runs", ["source_id"])
    op.create_index("ix_ingestion_runs_status", "ingestion_runs", ["status"])

    op.create_table(
        "raw_objects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("source_configs.id"), nullable=False),
        sa.Column("ingestion_run_id", sa.Integer(), sa.ForeignKey("ingestion_runs.id"), nullable=True),
        sa.Column("source_channel", sa.String(length=50), nullable=False),
        sa.Column("source_system", sa.String(length=100), nullable=False),
        sa.Column("external_object_type", sa.String(length=100), nullable=False),
        sa.Column("external_object_id", sa.String(length=255), nullable=True),
        sa.Column("external_parent_id", sa.String(length=255), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("event_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("original_filename", sa.String(length=255), nullable=True),
        sa.Column("content_type", sa.String(length=100), nullable=True),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=False),
        sa.Column("payload_storage_path", sa.String(length=500), nullable=False),
        sa.Column("raw_payload_ref", sa.String(length=500), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("parse_status", sa.String(length=50), nullable=False, server_default="not_parsed"),
        sa.Column("duplicate_status", sa.String(length=50), nullable=False, server_default="unique"),
        sa.Column("duplicate_of_id", sa.Integer(), sa.ForeignKey("raw_objects.id"), nullable=True),
        sa.Column("dedupe_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_raw_objects_id", "raw_objects", ["id"])
    op.create_index("ix_raw_objects_source_id", "raw_objects", ["source_id"])
    op.create_index("ix_raw_objects_ingestion_run_id", "raw_objects", ["ingestion_run_id"])
    op.create_index("ix_raw_objects_source_system", "raw_objects", ["source_system"])
    op.create_index("ix_raw_objects_external_object_type", "raw_objects", ["external_object_type"])
    op.create_index("ix_raw_objects_external_object_id", "raw_objects", ["external_object_id"])
    op.create_index("ix_raw_objects_checksum_sha256", "raw_objects", ["checksum_sha256"])

    op.create_table(
        "staging_gifts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("raw_object_id", sa.Integer(), sa.ForeignKey("raw_objects.id"), nullable=False),
        sa.Column("gift_id", sa.String(length=255), nullable=True),
        sa.Column("source_channel", sa.String(length=50), nullable=True),
        sa.Column("source_system", sa.String(length=100), nullable=True),
        sa.Column("source_file_id", sa.String(length=255), nullable=True),
        sa.Column("donor_name", sa.String(length=255), nullable=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("gift_date", sa.Date(), nullable=True),
        sa.Column("payment_type", sa.String(length=100), nullable=True),
        sa.Column("gift_type", sa.String(length=100), nullable=True),
        sa.Column("memo", sa.Text(), nullable=True),
        sa.Column("raw_payload_ref", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_staging_gifts_id", "staging_gifts", ["id"])
    op.create_index("ix_staging_gifts_raw_object_id", "staging_gifts", ["raw_object_id"])


def downgrade() -> None:
    op.drop_index("ix_staging_gifts_raw_object_id", table_name="staging_gifts")
    op.drop_index("ix_staging_gifts_id", table_name="staging_gifts")
    op.drop_table("staging_gifts")
    op.drop_index("ix_raw_objects_checksum_sha256", table_name="raw_objects")
    op.drop_index("ix_raw_objects_external_object_id", table_name="raw_objects")
    op.drop_index("ix_raw_objects_external_object_type", table_name="raw_objects")
    op.drop_index("ix_raw_objects_source_system", table_name="raw_objects")
    op.drop_index("ix_raw_objects_ingestion_run_id", table_name="raw_objects")
    op.drop_index("ix_raw_objects_source_id", table_name="raw_objects")
    op.drop_index("ix_raw_objects_id", table_name="raw_objects")
    op.drop_table("raw_objects")
    op.drop_index("ix_ingestion_runs_status", table_name="ingestion_runs")
    op.drop_index("ix_ingestion_runs_source_id", table_name="ingestion_runs")
    op.drop_index("ix_ingestion_runs_id", table_name="ingestion_runs")
    op.drop_table("ingestion_runs")
    op.drop_index("ix_source_configs_source_system", table_name="source_configs")
    op.drop_index("ix_source_configs_id", table_name="source_configs")
    op.drop_table("source_configs")

