"""Shared FastAPI dependencies."""

from collections.abc import Generator

from app.db.session import SessionLocal


def get_db() -> Generator:
    """Yield a transactional database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

