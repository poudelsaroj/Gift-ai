"""Every.org webhook-first connector."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.connectors.base.connector import BaseConnector
from app.connectors.base.types import FetchRequest, FetchResult
from app.connectors.everyorg.client import EveryOrgAPIClient
from app.connectors.everyorg.schemas import EveryOrgConfig


class EveryOrgConnector(BaseConnector):
    """Connector definition for Every.org donation ingestion."""

    source_system = "everyorg"
    acquisition_mode = "webhook"

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self.typed_config = EveryOrgConfig.model_validate(config)
        self.client = EveryOrgAPIClient(self.typed_config)

    def validate_config(self) -> None:
        """Validate the Every.org source config."""
        self.typed_config = EveryOrgConfig.model_validate(self.config)
        self.client = EveryOrgAPIClient(self.typed_config)

    def test_connection(self) -> dict[str, Any]:
        """Return the validated webhook configuration."""
        response = {
            "ok": True,
            "mode": self.typed_config.webhook_kind,
            "supported_objects": self.list_supported_objects(),
            "notes": [
                "Every.org donation data is delivered via webhook POSTs.",
                "Configure the webhook URL in Every.org with the source token query parameter.",
            ],
        }
        if self.typed_config.public_key and self.typed_config.nonprofit_slug:
            response["public_nonprofit"] = self.fetch_public_nonprofit()
        return response

    def fetch(self, request: FetchRequest) -> FetchResult:
        """Every.org donation ingestion is webhook-based, not pull-based."""
        raise NotImplementedError("Every.org donation ingestion uses webhooks; use the Every.org webhook endpoint.")

    def normalize_raw_metadata(self, payload: dict[str, Any] | list[Any] | str) -> dict[str, Any]:
        """Extract useful top-level metadata from Every.org webhook payloads."""
        if not isinstance(payload, dict):
            return {"preview": str(payload)[:200]}
        nonprofit = payload.get("toNonprofit") if isinstance(payload.get("toNonprofit"), dict) else {}
        fundraiser = payload.get("fromFundraiser") if isinstance(payload.get("fromFundraiser"), dict) else {}
        return {
            "top_level_keys": sorted(payload.keys()),
            "nonprofit_slug": nonprofit.get("slug"),
            "fundraiser_slug": fundraiser.get("slug"),
            "has_partner_metadata": bool(payload.get("partnerMetadata")),
        }

    def extract_external_ids(self, payload: dict[str, Any] | list[Any] | str) -> dict[str, str | None]:
        """Extract Every.org identifiers for dedupe and lineage."""
        if not isinstance(payload, dict):
            return {"external_object_id": None, "external_parent_id": None}
        fundraiser = payload.get("fromFundraiser") if isinstance(payload.get("fromFundraiser"), dict) else {}
        return {
            "external_object_id": str(payload.get("chargeId")) if payload.get("chargeId") else None,
            "external_parent_id": str(fundraiser.get("id"))
            if fundraiser.get("id")
            else (str(payload.get("partnerDonationId")) if payload.get("partnerDonationId") else None),
        }

    def list_supported_objects(self) -> list[str]:
        """Return supported Every.org object types."""
        return ["donation"]

    def parse_event_timestamp(self, payload: dict[str, Any]) -> datetime | None:
        """Parse the webhook donation timestamp when present."""
        value = payload.get("donationDate")
        if not isinstance(value, str):
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    def fetch_public_nonprofit(self) -> dict[str, Any]:
        """Fetch the public nonprofit profile from Every.org."""
        if not self.typed_config.public_key or not self.typed_config.nonprofit_slug:
            raise ValueError("public_key and nonprofit_slug are required for public Every.org fetches.")
        payload = self.client.get(f"/v0.2/nonprofit/{self.typed_config.nonprofit_slug}")
        return payload.get("data", {}).get("nonprofit", payload)
