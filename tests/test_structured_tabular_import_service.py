"""Tests for deterministic donation CSV parsing."""

from app.models.source_config import SourceConfig
from app.services.structured_tabular_import_service import StructuredTabularImportService


def test_parses_known_donation_export_schema() -> None:
    service = StructuredTabularImportService()
    source = SourceConfig(
        source_name="Manual CSV Uploads",
        source_system="csv",
        acquisition_mode="file_upload",
        auth_type="none",
        enabled=True,
        schedule="manual",
        config_json={},
    )
    content = (
        "source,name,email,donation_amount,currency,reason,payment_method,transaction_id,"
        "donation_date,donor_type,is_recurring,frequency,campaign_name,fund_designation,"
        "message,country,city,phone,tax_exempt,receipt_sent,metadata\n"
        'website,John Smith,john@example.com,100.00,USD,Education Support,credit_card,TXN001,'
        '2026-04-01,individual,false,one-time,Spring2026,General Fund,"Keep going",USA,New York,'
        '+1-555-0101,true,true,"{""utm_source"":""google""}"\n'
    ).encode("utf-8")

    extraction = service.extract(content=content, filename="donations.csv", source=source)

    assert extraction is not None
    assert extraction["is_gift_file"] is True
    assert extraction["gifts"][0]["sourceRecordId"] == "TXN001"
    assert extraction["gifts"][0]["sourceMedium"] == "website"
    assert extraction["gifts"][0]["campaignName"] == "Spring2026"
    assert extraction["gifts"][0]["relatedEntityName"] == "General Fund"
    assert extraction["gifts"][0]["extraMetadata"]["original_metadata"] == {"utm_source": "google"}


def test_returns_none_for_unknown_csv_shape() -> None:
    service = StructuredTabularImportService()
    source = SourceConfig(
        source_name="Manual CSV Uploads",
        source_system="csv",
        acquisition_mode="file_upload",
        auth_type="none",
        enabled=True,
        schedule="manual",
        config_json={},
    )
    content = b"first_name,last_name,total\nJohn,Smith,10\n"

    extraction = service.extract(content=content, filename="unknown.csv", source=source)

    assert extraction is None


def test_repairs_unquoted_metadata_column_fragments() -> None:
    service = StructuredTabularImportService()
    source = SourceConfig(
        source_name="Manual CSV Uploads",
        source_system="csv",
        acquisition_mode="file_upload",
        auth_type="none",
        enabled=True,
        schedule="manual",
        config_json={},
    )
    content = (
        "source,name,email,donation_amount,currency,reason,payment_method,transaction_id,"
        "donation_date,donor_type,is_recurring,frequency,campaign_name,fund_designation,"
        "message,country,city,phone,tax_exempt,receipt_sent,metadata\n"
        "website,John Smith,john@example.com,100.00,USD,Education Support,credit_card,TXN001,"
        "2026-04-01,individual,false,one-time,Spring2026,General Fund,Keep going,USA,New York,"
        "+1-555-0101,true,true,{\"utm_source\":\"google\",\"utm_medium\":\"cpc\"}\n"
    ).encode("utf-8")

    extraction = service.extract(content=content, filename="donations.csv", source=source)

    assert extraction is not None
    assert extraction["gifts"][0]["extraMetadata"]["original_metadata"] == {
        "utm_source": "google",
        "utm_medium": "cpc",
    }
