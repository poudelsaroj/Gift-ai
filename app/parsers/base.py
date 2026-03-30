"""Parser base hooks."""

from abc import ABC, abstractmethod
from typing import Any


class BaseParser(ABC):
    """Base parser abstraction for raw payload enrichment."""

    @abstractmethod
    def extract_metadata(self, payload: Any) -> dict[str, Any]:
        """Extract lightweight metadata from payloads."""

