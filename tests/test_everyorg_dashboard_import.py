"""Every.org dashboard CSV import tests."""

from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ingestion_run import IngestionRun
from app.models.raw_object import RawObject
from app.models.staging_gift import StagingGift


def everyorg_source_payload() -> dict:
    return {
        "source_name": "Every.org Donations",
        "source_system": "everyorg",
        "acquisition_mode": "webhook",
        "auth_type": "webhook",
        "enabled": True,
        "config_json": {
            "webhook_token": "everyorg-secret",
            "webhook_kind": "nonprofit",
            "nonprofit_slug": "demo-org",
        },
    }


def test_import_everyorg_dashboard_csv(client: TestClient, db_session: Session) -> None:
    created = client.post("/api/v1/sources", json=everyorg_source_payload()).json()
    csv_body = """Created,Donor,Email,Donation,Net,Notes/Testimony,Payment info,Fundraiser,Charge ID
12/30/2025,Ariana Gula,ariana.conti@gmail.com,$2500,$2500,,Card,Year End,charge-2500
09/21/2024,Anonymous Donor,,$100,$96.5,\"Private note from donor\",Bank transfer,,charge-100
"""

    response = client.post(
        f"/api/v1/everyorg/dashboard/sources/{created['id']}/imports/donations",
        files={"file": ("everyorg-donations.csv", csv_body, "text/csv")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["records_imported_count"] == 2
    assert body["source_filename"] == "everyorg-donations.csv"

    run = db_session.scalar(select(IngestionRun).where(IngestionRun.id == body["ingestion_run_id"]))
    assert run is not None
    assert run.status == "completed"
    assert run.records_fetched_count == 2

    raw_objects = list(
        db_session.scalars(
            select(RawObject)
            .where(RawObject.ingestion_run_id == body["ingestion_run_id"])
            .order_by(RawObject.id.asc())
        )
    )
    assert len(raw_objects) == 2
    assert raw_objects[0].external_object_type == "donation_export"
    assert raw_objects[0].external_object_id == "charge-2500"

    gifts = list(
        db_session.scalars(
            select(StagingGift)
            .where(StagingGift.raw_object_id.in_([item.id for item in raw_objects]))
            .order_by(StagingGift.id.asc())
        )
    )
    assert len(gifts) == 2
    assert gifts[0].record_type == "gift"
    assert gifts[0].source_record_id == "charge-2500"
    assert gifts[0].gift_id == "charge-2500"
    assert gifts[0].donor_name == "Ariana Gula"
    assert gifts[0].amount == Decimal("2500")
    assert gifts[0].currency == "USD"
    assert gifts[0].payment_type == "Card"
    assert gifts[0].source_file_id == "demo-org"
    assert gifts[0].memo == "Year End"
    assert gifts[0].extra_metadata["nonprofit_name"] == "Every.org Donations"
    assert gifts[1].gift_id == "charge-100"
    assert gifts[1].donor_name == "Anonymous Donor"
    assert gifts[1].amount == Decimal("100")
    assert gifts[1].payment_type == "Bank transfer"
