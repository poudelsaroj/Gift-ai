"""Connector registry and factory."""

from app.connectors.base.connector import BaseConnector
from app.connectors.email.connector import EmailConnector
from app.connectors.everyorg.connector import EveryOrgConnector
from app.connectors.onecause.connector import OneCauseConnector
from app.connectors.portal_export.connector import PortalExportConnector
from app.connectors.shared_folder.connector import SharedFolderConnector


class ConnectorRegistry:
    """Resolve connector classes by source system."""

    _registry: dict[str, type[BaseConnector]] = {
        "onecause": OneCauseConnector,
        "everyorg": EveryOrgConnector,
        "email": EmailConnector,
        "shared_folder": SharedFolderConnector,
        "portal_export": PortalExportConnector,
    }

    @classmethod
    def get_connector(cls, source_system: str, config: dict) -> BaseConnector:
        """Instantiate the connector registered for the source system."""
        try:
            connector_class = cls._registry[source_system]
        except KeyError as exc:
            raise ValueError(f"Unsupported source system: {source_system}") from exc
        return connector_class(config=config)

