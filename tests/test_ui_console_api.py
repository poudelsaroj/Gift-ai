"""Operator console API tests."""

from datetime import date, datetime
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.ingestion_run import IngestionRun
from app.models.raw_object import RawObject
from app.models.source_config import SourceConfig
from app.models.staging_gift import StagingGift


def test_console_state_reports_manual_csv_source_summary(client: TestClient, db_session: Session) -> None:
    source = SourceConfig(
        source_name="Manual CSV Uploads",
        source_system="csv",
        acquisition_mode="file_upload",
        auth_type="none",
        enabled=True,
        schedule="manual",
        config_json={"upload_path": "sample_data/uploads", "access_token": "secret-token"},
        parser_name="canonical_csv",
        dedupe_keys=["gift_id"],
        notes="Canonical spreadsheet imports",
    )
    db_session.add(source)
    db_session.flush()

    run = IngestionRun(
        source_id=source.id,
        run_type="incremental",
        trigger_type="manual",
        status="completed",
        started_at=datetime(2026, 4, 7, 9, 0, 0),
        completed_at=datetime(2026, 4, 7, 9, 3, 0),
        records_fetched_count=1,
        duplicates_detected_count=0,
    )
    db_session.add(run)
    db_session.flush()

    raw_object = RawObject(
        source_id=source.id,
        ingestion_run_id=run.id,
        source_channel="file_upload",
        source_system="csv",
        external_object_type="gift_extract",
        external_object_id="upload-row-1",
        external_parent_id="manual-import-1",
        fetched_at=datetime(2026, 4, 7, 9, 1, 0),
        event_timestamp=datetime(2026, 4, 7, 9, 1, 0),
        original_filename="gifts.csv",
        content_type="text/csv",
        checksum_sha256="a" * 64,
        payload_storage_path="raw/csv/gifts.csv",
        raw_payload_ref="raw/csv/gifts.csv",
        metadata_json={"sheet_name": "Sheet1"},
        parse_status="parsed",
        duplicate_status="unique",
    )
    db_session.add(raw_object)
    db_session.flush()

    record = StagingGift(
        raw_object_id=raw_object.id,
        record_type="gift",
        source_record_id="csv-001",
        gift_id="gift-001",
        source_channel="file_upload",
        source_system="csv",
        source_file_id="gifts.csv",
        primary_name="Manual Donor",
        primary_email="manual@example.com",
        donor_name="Manual Donor",
        donor_email="manual@example.com",
        amount=Decimal("25.50"),
        currency="USD",
        record_date=date(2026, 4, 7),
        gift_date=date(2026, 4, 7),
        campaign_name="Spring Drive",
        receipt_number="R-100",
        raw_payload_ref="raw/csv/gifts.csv",
        status="extracted",
        duplicate_status="unique",
        confidence_score=0.98,
        extra_metadata={"import_batch": "batch-1"},
    )
    db_session.add(record)
    db_session.commit()

    response = client.get("/api/v1/ui/console-state")
    assert response.status_code == 200

    body = response.json()
    assert body["summary"]["total_sources"] == 1
    assert body["summary"]["total_records"] == 1
    assert body["summary"]["total_gift_records"] == 1
    assert body["summary"]["total_raw_objects"] == 1
    assert len(body["recent_runs"]) == 1

    source_summary = body["sources"][0]
    assert source_summary["source_name"] == "Manual CSV Uploads"
    assert source_summary["workflow_label"] == "Manual CSV, TSV, or XLSX import"
    assert source_summary["primary_action_label"] == "Upload file"
    assert source_summary["supports_manual_upload"] is True
    assert source_summary["supports_direct_trigger"] is False
    assert source_summary["raw_object_count"] == 1
    assert source_summary["record_count"] == 1
    assert source_summary["gift_record_count"] == 1
    assert source_summary["raw_object_types"] == ["gift_extract"]
    assert source_summary["record_status_values"] == ["extracted"]
    assert source_summary["config_json"]["access_token"] == "***REDACTED***"
    assert source_summary["latest_run"]["status"] == "completed"


def test_operator_records_endpoint_uses_common_canonical_model_for_manual_csv(
    client: TestClient,
    db_session: Session,
) -> None:
    source = SourceConfig(
        source_name="Manual CSV Uploads",
        source_system="csv",
        acquisition_mode="file_upload",
        auth_type="none",
        enabled=True,
        schedule="manual",
        config_json={},
    )
    db_session.add(source)
    db_session.flush()

    raw_object = RawObject(
        source_id=source.id,
        ingestion_run_id=None,
        source_channel="file_upload",
        source_system="csv",
        external_object_type="gift_extract",
        external_object_id="row-2",
        external_parent_id="upload-2",
        fetched_at=datetime(2026, 4, 7, 10, 0, 0),
        event_timestamp=datetime(2026, 4, 7, 10, 0, 0),
        original_filename="manual.csv",
        content_type="text/csv",
        checksum_sha256="b" * 64,
        payload_storage_path="raw/csv/manual.csv",
        raw_payload_ref="raw/csv/manual.csv",
        metadata_json={"row_number": 2},
        parse_status="parsed",
        duplicate_status="unique",
    )
    db_session.add(raw_object)
    db_session.flush()

    db_session.add(
        StagingGift(
            raw_object_id=raw_object.id,
            record_type="gift",
            source_record_id="csv-002",
            source_system="csv",
            source_channel="file_upload",
            primary_name="Another Donor",
            primary_email="another@example.com",
            amount=Decimal("100.00"),
            currency="USD",
            record_date=date(2026, 4, 6),
            campaign_name="Annual Appeal",
            receipt_number="R-101",
            status="extracted",
            duplicate_status="unique",
            extra_metadata={"uploaded_by": "operator"},
        )
    )
    db_session.commit()

    response = client.get(
        f"/api/v1/ui/records?source_id={source.id}&status=extracted&search=another@example.com"
    )
    assert response.status_code == 200

    records = response.json()
    assert len(records) == 1
    assert records[0]["source_id"] == source.id
    assert records[0]["source_name"] == "Manual CSV Uploads"
    assert records[0]["source_system"] == "csv"
    assert records[0]["record_type"] == "gift"
    assert records[0]["status"] == "extracted"
    assert records[0]["primary_email"] == "another@example.com"
    assert records[0]["record_date"] == "2026-04-06"
