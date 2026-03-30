"""Raw object endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import get_settings
from app.schemas.common import PaginatedResponse
from app.schemas.raw_object import RawObjectPayloadResponse, RawObjectRead
from app.services.raw_object_service import RawObjectService
from app.storage.filesystem import FilesystemStorage

router = APIRouter(prefix="/api/v1/raw-objects")
raw_object_service = RawObjectService()
storage = FilesystemStorage(get_settings().raw_storage_root)


@router.get("", response_model=PaginatedResponse[RawObjectRead])
def list_raw_objects(
    db: Session = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> PaginatedResponse[RawObjectRead]:
    """List raw objects."""
    items, total = raw_object_service.list(db, offset=offset, limit=limit)
    return PaginatedResponse[RawObjectRead](items=items, total=total)


@router.get("/{raw_object_id}", response_model=RawObjectRead)
def get_raw_object(raw_object_id: int, db: Session = Depends(get_db)) -> RawObjectRead:
    """Get a raw object."""
    raw_object = raw_object_service.get(db, raw_object_id)
    if not raw_object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Raw object not found")
    return raw_object


@router.get("/{raw_object_id}/payload", response_model=RawObjectPayloadResponse)
def get_raw_object_payload(raw_object_id: int, db: Session = Depends(get_db)) -> RawObjectPayloadResponse:
    """Fetch the stored raw payload."""
    raw_object = raw_object_service.get(db, raw_object_id)
    if not raw_object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Raw object not found")
    payload = storage.get_payload(raw_object.payload_storage_path)
    return RawObjectPayloadResponse(raw_object_id=raw_object_id, payload=payload)


@router.post("/{raw_object_id}/reprocess", response_model=RawObjectRead)
def reprocess_raw_object(raw_object_id: int, db: Session = Depends(get_db)) -> RawObjectRead:
    """Stub reprocess endpoint for future parser workflows."""
    raw_object = raw_object_service.get(db, raw_object_id)
    if not raw_object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Raw object not found")
    raw_object.parse_status = "reprocess_requested"
    db.add(raw_object)
    db.commit()
    db.refresh(raw_object)
    return raw_object
