"""Source management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.connectors.registry import ConnectorRegistry
from app.connectors.onecause.config_resolver import resolve_onecause_config
from app.models.source_config import SourceConfig
from app.schemas.common import PaginatedResponse
from app.schemas.ingestion_run import IngestionRunRead
from app.schemas.source import (
    SourceConfigCreate,
    SourceConfigRead,
    SourceConfigUpdate,
    SourceTestResponse,
    TriggerIngestionRequest,
    TriggerIngestionResponse,
)
from app.services.ingestion_service import IngestionService
from app.services.source_service import SourceService

router = APIRouter(prefix="/api/v1/sources")
source_service = SourceService()
ingestion_service = IngestionService()


def _get_source_or_404(db: Session, source_id: int) -> SourceConfig:
    source = source_service.get(db, source_id)
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    return source


@router.post("", response_model=SourceConfigRead, status_code=status.HTTP_201_CREATED)
def create_source(payload: SourceConfigCreate, db: Session = Depends(get_db)) -> SourceConfig:
    """Create a source config."""
    source_payload = payload
    if payload.source_system == "onecause":
        try:
            source_payload = payload.model_copy(
                update={"config_json": resolve_onecause_config(payload.config_json)}
            )
        except (ValidationError, ValueError) as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    try:
        connector = ConnectorRegistry.get_connector(source_payload.source_system, source_payload.config_json)
        connector.validate_config()
    except (ValidationError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return source_service.create(db, source_payload)


@router.get("", response_model=PaginatedResponse[SourceConfigRead])
def list_sources(
    db: Session = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> PaginatedResponse[SourceConfigRead]:
    """List sources."""
    items, total = source_service.list(db, offset=offset, limit=limit)
    return PaginatedResponse[SourceConfigRead](items=items, total=total)


@router.get("/{source_id}", response_model=SourceConfigRead)
def get_source(source_id: int, db: Session = Depends(get_db)) -> SourceConfig:
    """Get a source."""
    return _get_source_or_404(db, source_id)


@router.patch("/{source_id}", response_model=SourceConfigRead)
def update_source(
    source_id: int,
    payload: SourceConfigUpdate,
    db: Session = Depends(get_db),
) -> SourceConfig:
    """Patch a source config."""
    source = _get_source_or_404(db, source_id)
    updated_config = source.config_json if payload.config_json is None else payload.config_json
    if source.source_system == "onecause":
        try:
            updated_config = resolve_onecause_config(updated_config)
        except (ValidationError, ValueError) as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    try:
        connector = ConnectorRegistry.get_connector(source.source_system, updated_config)
        connector.validate_config()
    except (ValidationError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    if payload.config_json is not None and source.source_system == "onecause":
        payload = payload.model_copy(update={"config_json": updated_config})
    return source_service.update(db, source, payload)


@router.post("/{source_id}/test", response_model=SourceTestResponse)
def test_source(source_id: int, db: Session = Depends(get_db)) -> SourceTestResponse:
    """Test source connectivity."""
    source = _get_source_or_404(db, source_id)
    try:
        connector = ConnectorRegistry.get_connector(source.source_system, source.config_json)
        connector.validate_config()
    except (ValidationError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    details = connector.test_connection()
    return SourceTestResponse(ok=True, source_id=source_id, details=details)


@router.post("/{source_id}/trigger", response_model=TriggerIngestionResponse)
def trigger_source(
    source_id: int,
    payload: TriggerIngestionRequest,
    db: Session = Depends(get_db),
) -> TriggerIngestionResponse:
    """Trigger an ingestion run for a source."""
    source = _get_source_or_404(db, source_id)
    run = ingestion_service.execute(
        db,
        source,
        run_type=payload.run_type,
        trigger_type=payload.trigger_type,
        object_types=payload.object_types,
        start_time=payload.start_time,
        end_time=payload.end_time,
    )
    return TriggerIngestionResponse(
        ingestion_run_id=run.id,
        status=run.status,
        records_fetched_count=run.records_fetched_count,
        duplicates_detected_count=run.duplicates_detected_count,
        cursor_state=run.cursor_state,
    )


@router.get("/{source_id}/ingestion-runs", response_model=PaginatedResponse[IngestionRunRead])
def list_source_runs(
    source_id: int,
    db: Session = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> PaginatedResponse[IngestionRunRead]:
    """List runs for a given source."""
    _get_source_or_404(db, source_id)
    items, total = ingestion_service.list_runs_for_source(db, source_id, offset=offset, limit=limit)
    return PaginatedResponse[IngestionRunRead](items=items, total=total)


@router.post("/{source_id}/sync/onecause/paid-activities", response_model=TriggerIngestionResponse)
def sync_onecause_paid_activities(source_id: int, db: Session = Depends(get_db)) -> TriggerIngestionResponse:
    """Trigger OneCause paid activities sync."""
    return trigger_source(
        source_id,
        TriggerIngestionRequest(object_types=["paid_activities"]),
        db,
    )


@router.post("/{source_id}/sync/onecause/supporters", response_model=TriggerIngestionResponse)
def sync_onecause_supporters(source_id: int, db: Session = Depends(get_db)) -> TriggerIngestionResponse:
    """Trigger OneCause supporter sync."""
    return trigger_source(
        source_id,
        TriggerIngestionRequest(object_types=["supporters"]),
        db,
    )


@router.post("/{source_id}/sync/onecause/full", response_model=TriggerIngestionResponse)
def sync_onecause_full(source_id: int, db: Session = Depends(get_db)) -> TriggerIngestionResponse:
    """Trigger full OneCause sync."""
    return trigger_source(
        source_id,
        TriggerIngestionRequest(
            object_types=["paid_activities", "supporters", "events", "fundraising_pages"],
            run_type="full",
        ),
        db,
    )
