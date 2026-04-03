"""Normalized read model endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.normalized import NormalizedGiftRead, NormalizedRecordRead, NormalizedSupporterRead
from app.services.normalization_service import NormalizationService

router = APIRouter(prefix="/api/v1/normalized")
normalization_service = NormalizationService()


@router.get("/records", response_model=PaginatedResponse[NormalizedRecordRead])
def list_normalized_records(
    db: Session = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> PaginatedResponse[NormalizedRecordRead]:
    items, total = normalization_service.list_records(db, offset=offset, limit=limit)
    return PaginatedResponse[NormalizedRecordRead](items=items, total=total)


@router.get("/gifts", response_model=PaginatedResponse[NormalizedGiftRead])
def list_normalized_gifts(
    db: Session = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> PaginatedResponse[NormalizedGiftRead]:
    items, total = normalization_service.list_gifts(db, offset=offset, limit=limit)
    return PaginatedResponse[NormalizedGiftRead](items=items, total=total)


@router.get("/supporters", response_model=PaginatedResponse[NormalizedSupporterRead])
def list_normalized_supporters(
    db: Session = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> PaginatedResponse[NormalizedSupporterRead]:
    items, total = normalization_service.list_supporters(db, offset=offset, limit=limit)
    return PaginatedResponse[NormalizedSupporterRead](items=items, total=total)
