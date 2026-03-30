"""Ingestion run endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.ingestion_run import IngestionRunRead
from app.services.ingestion_service import IngestionService

router = APIRouter(prefix="/api/v1/ingestion-runs")
ingestion_service = IngestionService()


@router.get("", response_model=PaginatedResponse[IngestionRunRead])
def list_ingestion_runs(
    db: Session = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> PaginatedResponse[IngestionRunRead]:
    """List ingestion runs."""
    items, total = ingestion_service.list_runs(db, offset=offset, limit=limit)
    return PaginatedResponse[IngestionRunRead](items=items, total=total)


@router.get("/{run_id}", response_model=IngestionRunRead)
def get_ingestion_run(run_id: int, db: Session = Depends(get_db)) -> IngestionRunRead:
    """Get an ingestion run."""
    run = ingestion_service.get_run(db, run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingestion run not found")
    return run
