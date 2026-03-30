"""Source configuration service."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.source_config import SourceConfig
from app.schemas.source import SourceConfigCreate, SourceConfigUpdate


class SourceService:
    """CRUD operations for source configurations."""

    def create(self, db: Session, payload: SourceConfigCreate) -> SourceConfig:
        source = SourceConfig(**payload.model_dump())
        db.add(source)
        db.commit()
        db.refresh(source)
        return source

    def list(self, db: Session, offset: int = 0, limit: int = 100) -> tuple[list[SourceConfig], int]:
        items = list(db.scalars(select(SourceConfig).offset(offset).limit(limit)))
        total = db.scalar(select(func.count()).select_from(SourceConfig)) or 0
        return items, total

    def get(self, db: Session, source_id: int) -> SourceConfig | None:
        return db.get(SourceConfig, source_id)

    def update(self, db: Session, source: SourceConfig, payload: SourceConfigUpdate) -> SourceConfig:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(source, field, value)
        db.add(source)
        db.commit()
        db.refresh(source)
        return source

