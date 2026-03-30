"""Common response schemas."""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ORMModel(BaseModel):
    """Base schema with ORM support."""

    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(ORMModel, Generic[T]):
    """Simple paginated response wrapper."""

    items: list[T]
    total: int

