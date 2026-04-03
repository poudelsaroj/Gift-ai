"""Pledge CSV import tests."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ingestion_run import IngestionRun
from app.models.raw_object import RawObject
from app.models.staging_gift import StagingGift


def pledge_source_payload() -> dict:
    return {
        "source_name": "Pledge Donations",
        "source_system": "pledge",
        "acquisition_mode": "api",
        "auth_type": "bearer",
        "enabled": True,
        "config_json": {
            "api_base_url": "https://api.pledge.example",
            "api_key": "pledge-secret",
        },
    }


def test_import_pledge_csv(client, db_session: Session) -> None:
    created = client.post("/api/v1/sources", json=pledge_source_payload()).json()
    csv_body = """ID,Date,Fundraiser name,Fundraiser URL,Donor first name,Donor last name,Donor email,Source,Frequency,Gross amount,Net amount,Payment method,Campaign ID,Project Designation,Donor ID,Payout ID
don_1,03/02/26 4:17 PM,,https://example.org/fundraiser,Nancy,Hettwer,jh@example.org,Legacy.com,One-time,$100.00,$96.80,Credit Card,camp_1,ALS Care,donor_1,payout_1
don_2,02/17/26 10:08 AM,,,,,N/A,Legacy.com,One-time,$300.00,$291.00,Credit Card,camp_2,,donor_2,payout_2
"""

    response = client.post(
        f"/api/v1/pledge/sources/{created['id']}/imports/donations",
        files={"file": ("pledge-donations.csv", csv_body, "text/csv")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["records_imported_count"] == 2

    run = db_session.scalar(select(IngestionRun).where(IngestionRun.id == body["ingestion_run_id"]))
    assert run is not None
    assert run.status == "completed"

    raw_objects = list(
        db_session.scalars(
            select(RawObject)
            .where(RawObject.ingestion_run_id == body["ingestion_run_id"])
            .order_by(RawObject.id.asc())
        )
    )
    assert len(raw_objects) == 2
    assert raw_objects[0].external_object_type == "donations"
    assert raw_objects[0].external_object_id == "don_1"

    gifts = list(
        db_session.scalars(
            select(StagingGift)
            .where(StagingGift.raw_object_id.in_([item.id for item in raw_objects]))
            .order_by(StagingGift.id.asc())
        )
    )
    assert len(gifts) == 2
    assert gifts[0].source_system == "pledge"
    assert gifts[0].source_record_id == "don_1"
    assert gifts[0].donor_name == "Nancy Hettwer"
    assert gifts[0].donor_email == "jh@example.org"
    assert gifts[0].amount == Decimal("100.00")
    assert gifts[0].payment_type == "Credit Card"
    assert gifts[0].memo == "ALS Care"
    assert gifts[1].source_record_id == "don_2"
    assert gifts[1].donor_name == "Legacy.com"
