"""Generic file-upload import endpoints backed by OpenAI extraction."""

from __future__ import annotations

import base64
import hashlib
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.connectors.base.types import RawFetchItem
from app.models.source_config import SourceConfig
from app.services.ingestion_service import IngestionService
from app.services.openai_tabular_import_service import OpenAITabularImportService
from app.services.source_service import SourceService

router = APIRouter(prefix="/api/v1/files")
source_service = SourceService()
ingestion_service = IngestionService()
import_service = OpenAITabularImportService()


class FileImportResponse(BaseModel):
    """Response for generic file imports."""

    ok: bool
    source_id: int
    ingestion_run_id: int
    records_imported_count: int
    duplicates_detected_count: int
    source_filename: str | None


def _get_source_or_404(db: Session, source_id: int) -> SourceConfig:
    source = source_service.get(db, source_id)
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    return source


@router.post("/sources/{source_id}/imports/canonical", response_model=FileImportResponse)
async def import_canonical_file(
    source_id: int,
    file: Annotated[UploadFile, File(...)],
    db: Annotated[Session, Depends(get_db)],
) -> FileImportResponse:
    """Upload a CSV/TSV/XLSX file and normalize gift rows into canonical data."""
    source = _get_source_or_404(db, source_id)
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Upload a file.")
    extension = _extension(file.filename)
    if extension not in {".csv", ".tsv", ".xlsx"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Upload a CSV, TSV, or XLSX file.",
        )

    content = await file.read()
    extraction = import_service.extract(
        content=content,
        filename=file.filename,
        content_type=file.content_type,
        source=source,
    )
    if not extraction.get("is_gift_file"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The uploaded file did not contain recognizable gift rows.",
        )

    items = _build_import_items(
        source=source,
        filename=file.filename,
        content=content,
        content_type=file.content_type,
        extraction=extraction,
    )
    if len(items) <= 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No gift rows were extracted from the uploaded file.",
        )

    run = ingestion_service.ingest_items(
        db,
        source,
        items=items,
        run_type="full",
        trigger_type="manual_upload",
        metadata_json={
            "import_kind": "canonical_tabular_openai",
            "source_filename": file.filename,
            "imported_rows": len(items) - 1,
            "extraction_summary": extraction.get("summary"),
        },
    )
    return FileImportResponse(
        ok=True,
        source_id=source.id,
        ingestion_run_id=run.id,
        records_imported_count=run.records_fetched_count,
        duplicates_detected_count=run.duplicates_detected_count,
        source_filename=file.filename,
    )


def _build_import_items(
    *,
    source: SourceConfig,
    filename: str,
    content: bytes,
    content_type: str | None,
    extraction: dict,
) -> list[RawFetchItem]:
    now = datetime.now(tz=UTC)
    file_id = hashlib.sha1(content).hexdigest()[:24]
    items: list[RawFetchItem] = [
        RawFetchItem(
            object_type="uploaded_file",
            external_object_id=file_id,
            external_parent_id=None,
            payload={
                "filename": filename,
                "mimeType": content_type or "application/octet-stream",
                "size": len(content),
                "contentBase64": base64.b64encode(content).decode("ascii"),
                "summary": extraction.get("summary"),
            },
            event_timestamp=now,
            content_type=content_type or "application/octet-stream",
            source_channel="manual_upload",
            original_filename=filename,
            metadata={"import_kind": "canonical_tabular_openai"},
        )
    ]
    for index, gift in enumerate(extraction.get("gifts") or [], start=1):
        if not isinstance(gift, dict):
            continue
        payload = dict(gift)
        payload.setdefault("recordType", "gift")
        payload.setdefault("sourceFileId", filename)
        payload.setdefault("sourceFilename", filename)
        payload.setdefault("sourceMedium", "uploaded_file")
        payload.setdefault("sourceParentId", file_id)
        source_record_id = payload.get("sourceRecordId") or str(index)
        payload.setdefault("sourceRecordId", source_record_id)
        payload.setdefault("giftId", payload.get("giftId") or str(index))
        items.append(
            RawFetchItem(
                object_type="gift_extract",
                external_object_id=str(payload.get("sourceRecordId")),
                external_parent_id=file_id,
                payload=payload,
                event_timestamp=now,
                content_type="application/json",
                source_channel="manual_upload",
                original_filename=filename,
                metadata={"import_kind": "canonical_tabular_openai", "row_number": index},
            )
        )
    return items


def _extension(filename: str) -> str:
    lowered = filename.lower()
    if "." not in lowered:
        return ""
    return lowered[lowered.rfind(".") :]
