"""Connector registry and factory."""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from collections.abc import Iterable

import app.connectors as connector_packages
from app.connectors.base.connector import BaseConnector


class ConnectorRegistry:
    """Resolve connector classes by source system."""

    _BUILTIN_CONNECTOR_MODULES = (
        "app.connectors.csv.connector",
        "app.connectors.email.connector",
        "app.connectors.everyorg.connector",
        "app.connectors.gmail.connector",
        "app.connectors.onecause.connector",
        "app.connectors.pledge.connector",
        "app.connectors.portal_export.connector",
        "app.connectors.shared_folder.connector",
    )
    _registry: dict[str, type[BaseConnector]] = {}
    _discovered = False

    @classmethod
    def register(cls, connector_class: type[BaseConnector]) -> None:
        """Register a connector class explicitly."""
        source_system = getattr(connector_class, "source_system", None)
        if not source_system:
            raise ValueError("Connector classes must define source_system.")
        cls._registry[str(source_system)] = connector_class

    @classmethod
    def create_connector(cls, source_system: str, config: dict) -> BaseConnector:
        """Instantiate the connector registered for the source system."""
        cls._ensure_discovered()
        try:
            connector_class = cls._registry[source_system]
        except KeyError as exc:
            raise ValueError(f"Unsupported source system: {source_system}") from exc
        return connector_class(config=config)

    @classmethod
    def get_connector(cls, source_system: str, config: dict) -> BaseConnector:
        """Backward-compatible alias for connector creation."""
        return cls.create_connector(source_system, config)

    @classmethod
    def supported_source_systems(cls) -> list[str]:
        """Return the sorted list of supported source systems."""
        cls._ensure_discovered()
        return sorted(cls._registry)

    @classmethod
    def _ensure_discovered(cls) -> None:
        if cls._discovered:
            return
        cls._discover_connectors()
        cls._discovered = True

    @classmethod
    def _discover_connectors(cls) -> None:
        for module_name in cls._BUILTIN_CONNECTOR_MODULES:
            module = importlib.import_module(module_name)
            cls._register_module_connectors(module)
        for package_name in cls._connector_package_names():
            module_name = f"{connector_packages.__name__}.{package_name}.connector"
            try:
                module = importlib.import_module(module_name)
            except ModuleNotFoundError:
                continue
            cls._register_module_connectors(module)

    @staticmethod
    def _connector_package_names() -> Iterable[str]:
        for module_info in pkgutil.iter_modules(connector_packages.__path__):
            if module_info.ispkg and module_info.name not in {"base"}:
                yield module_info.name

    @classmethod
    def _register_module_connectors(cls, module: object) -> None:
        for _, candidate in inspect.getmembers(module, inspect.isclass):
            if not issubclass(candidate, BaseConnector) or candidate is BaseConnector:
                continue
            if candidate.__module__ != getattr(module, "__name__", ""):
                continue
            cls.register(candidate)
