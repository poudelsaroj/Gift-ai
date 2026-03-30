"""Connector dataclasses and protocols."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class FetchRequest:
    """Standard fetch request passed to connectors."""

    run_type: str
    trigger_type: str
    object_types: list[str] | None = None
    cursor_state: dict[str, Any] | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None


@dataclass(slots=True)
class RawFetchItem:
    """Connector-emitted raw item."""

    object_type: str
    external_object_id: str | None
    payload: dict[str, Any] | list[Any] | str
    event_timestamp: datetime | None = None
    external_parent_id: str | None = None
    content_type: str = "application/json"
    source_channel: str = "api"
    original_filename: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class FetchResult:
    """Connector fetch response."""

    items: list[RawFetchItem]
    cursor_state: dict[str, Any] | None
    metadata: dict[str, Any] = field(default_factory=dict)

