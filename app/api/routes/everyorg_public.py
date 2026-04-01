"""Every.org public-data endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.connectors.everyorg.config_resolver import resolve_everyorg_config
from app.connectors.everyorg.connector import EveryOrgConnector
from app.services.source_service import SourceService

router = APIRouter(prefix="/api/v1/everyorg")
source_service = SourceService()


class EveryOrgPublicNonprofitResponse(BaseModel):
    """Public nonprofit profile returned from Every.org."""

    source_id: int
    nonprofit: dict[str, Any]


@router.get("/sources/{source_id}/nonprofit", response_model=EveryOrgPublicNonprofitResponse)
def get_everyorg_public_nonprofit(
    source_id: int,
    db: Session = Depends(get_db),
) -> EveryOrgPublicNonprofitResponse:
    """Fetch a source's Every.org public nonprofit profile."""
    source = source_service.get(db, source_id)
    if not source or source.source_system != "everyorg":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Every.org source not found")

    try:
        config = resolve_everyorg_config(source.config_json)
        connector = EveryOrgConnector(config)
        connector.validate_config()
        nonprofit = connector.fetch_public_nonprofit()
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return EveryOrgPublicNonprofitResponse(source_id=source.id, nonprofit=nonprofit)
