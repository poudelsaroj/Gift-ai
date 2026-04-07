"""Base connector contract."""

from abc import ABC, abstractmethod
from typing import Any

from app.connectors.base.types import FetchRequest, FetchResult


class BaseConnector(ABC):
    """Abstract connector contract for all acquisition patterns."""

    source_system: str
    acquisition_mode: str

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    @abstractmethod
    def validate_config(self) -> None:
        """Validate connector-specific config."""

    @abstractmethod
    def test_connection(self) -> dict[str, Any]:
        """Perform a lightweight connectivity check."""

    @abstractmethod
    def fetch(self, request: FetchRequest) -> FetchResult:
        """Fetch raw data for the given request."""

    def fetch_incremental(self, request: FetchRequest) -> FetchResult:
        """Default incremental behavior delegates to fetch."""
        return self.fetch(request)

    def runtime_config_updates(self) -> dict[str, Any] | None:
        """Return connector-generated config updates worth persisting."""
        return None

    @abstractmethod
    def normalize_raw_metadata(self, payload: dict[str, Any] | list[Any] | str) -> dict[str, Any]:
        """Extract light metadata for raw payload tracking."""

    @abstractmethod
    def extract_external_ids(self, payload: dict[str, Any] | list[Any] | str) -> dict[str, str | None]:
        """Extract source-specific identifiers."""

    @abstractmethod
    def list_supported_objects(self) -> list[str]:
        """Return supported object types for the connector."""

