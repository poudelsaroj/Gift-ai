"""Every.org dashboard export import endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.source_config import SourceConfig
from app.services.everyorg_dashboard_import_service import EveryOrgDashboardImportService
from app.services.ingestion_service import IngestionService
from app.services.source_service import SourceService

router = APIRouter(prefix="/api/v1/everyorg/dashboard")
source_service = SourceService()
ingestion_service = IngestionService()
import_service = EveryOrgDashboardImportService()


class EveryOrgDashboardImportResponse(BaseModel):
    """Response for dashboard donation imports."""

    ok: bool
    source_id: int
    ingestion_run_id: int
    records_imported_count: int
    duplicates_detected_count: int
    source_filename: str | None


def _get_everyorg_source_or_404(db: Session, source_id: int) -> SourceConfig:
    source = source_service.get(db, source_id)
    if not source or source.source_system != "everyorg":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Every.org source not found",
        )
    return source


@router.post(
    "/sources/{source_id}/imports/donations",
    response_model=EveryOrgDashboardImportResponse,
)
async def import_everyorg_dashboard_donations(
    source_id: int,
    file: Annotated[UploadFile, File(...)],
    db: Annotated[Session, Depends(get_db)],
) -> EveryOrgDashboardImportResponse:
    """Import an Every.org dashboard donation CSV export."""
    source = _get_everyorg_source_or_404(db, source_id)
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Upload a CSV export file.",
        )

    content = await file.read()
    items = import_service.parse_csv(content, filename=file.filename, source=source)
    if not items:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No donation rows were parsed from the CSV export.",
        )

    run = ingestion_service.ingest_items(
        db,
        source,
        items=items,
        run_type="full",
        trigger_type="manual_upload",
        metadata_json={
            "import_kind": "everyorg_dashboard_csv",
            "source_filename": file.filename,
            "imported_rows": len(items),
        },
    )
    return EveryOrgDashboardImportResponse(
        ok=True,
        source_id=source.id,
        ingestion_run_id=run.id,
        records_imported_count=run.records_fetched_count,
        duplicates_detected_count=run.duplicates_detected_count,
        source_filename=file.filename,
    )
