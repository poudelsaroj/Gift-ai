"""Storage abstraction."""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any


class BaseStorage(ABC):
    """Abstract raw payload storage interface."""

    @abstractmethod
    def save_json_payload(
        self,
        *,
        source_system: str,
        run_id: int,
        object_type: str,
        object_id: str | None,
        payload: dict[str, Any] | list[Any],
        fetched_at: datetime,
    ) -> str:
        """Persist a JSON payload."""

    @abstractmethod
    def save_binary_file(
        self,
        *,
        source_system: str,
        run_id: int,
        object_type: str,
        object_id: str | None,
        filename: str,
        content: bytes,
        fetched_at: datetime,
    ) -> str:
        """Persist binary content."""

    @abstractmethod
    def get_payload(self, path: str) -> dict[str, Any] | str:
        """Retrieve a stored payload."""

    @abstractmethod
    def build_storage_path(
        self,
        *,
        source_system: str,
        fetched_at: datetime,
        run_id: int,
        object_type: str,
        object_id: str | None,
        extension: str,
    ) -> Path:
        """Build storage path for a raw payload."""

