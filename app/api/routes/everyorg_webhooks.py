"""Every.org webhook ingestion endpoints."""

from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.connectors.everyorg.connector import EveryOrgConnector
from app.connectors.everyorg.schemas import EveryOrgDonationWebhookPayload
from app.models.source_config import SourceConfig
from app.services.ingestion_service import IngestionService
from app.services.source_service import SourceService

router = APIRouter(prefix="/api/v1/webhooks/everyorg")
source_service = SourceService()
ingestion_service = IngestionService()


class EveryOrgWebhookResponse(BaseModel):
    """Webhook ingestion acknowledgement."""

    ok: bool
    source_id: int
    ingestion_run_id: int
    raw_object_id: int
    duplicate_status: str


def _get_source_or_404(db: Session, source_id: int) -> SourceConfig:
    source = source_service.get(db, source_id)
    if not source or source.source_system != "everyorg":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Every.org source not found")
    return source


@router.post("/{source_id}", response_model=EveryOrgWebhookResponse)
def receive_everyorg_webhook(
    source_id: int,
    payload: EveryOrgDonationWebhookPayload,
    token: str = Query(..., min_length=8),
    db: Session = Depends(get_db),
) -> EveryOrgWebhookResponse:
    """Receive and persist an Every.org donation webhook."""
    source = _get_source_or_404(db, source_id)
    connector = EveryOrgConnector(source.config_json)

    if not secrets.compare_digest(token, connector.typed_config.webhook_token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid webhook token")

    if connector.typed_config.nonprofit_slug:
        incoming_slug = payload.toNonprofit.slug.strip().lower()
        expected_slug = connector.typed_config.nonprofit_slug.strip().lower()
        if incoming_slug != expected_slug:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Webhook nonprofit slug does not match source configuration",
            )

    payload_dict = payload.model_dump(mode="json", exclude_none=True)
    ids = connector.extract_external_ids(payload_dict)
    event_timestamp = connector.parse_event_timestamp(payload_dict)
    metadata = connector.normalize_raw_metadata(payload_dict)
    run, raw_object = ingestion_service.ingest_webhook_payload(
        db,
        source,
        object_type="donation",
        payload=payload_dict,
        external_object_id=ids["external_object_id"],
        external_parent_id=ids["external_parent_id"],
        event_timestamp=event_timestamp,
        metadata_json=metadata,
    )
    return EveryOrgWebhookResponse(
        ok=True,
        source_id=source.id,
        ingestion_run_id=run.id,
        raw_object_id=raw_object.id,
        duplicate_status=raw_object.duplicate_status,
    )
