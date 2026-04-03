"""Pledge API connector."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.connectors.base.connector import BaseConnector
from app.connectors.base.types import FetchRequest, FetchResult, RawFetchItem
from app.connectors.pledge.client import PledgeAPIClient
from app.connectors.pledge.schemas import PledgeConfig


class PledgeConnector(BaseConnector):
    """API connector for Pledge donation ingestion."""

    source_system = "pledge"
    acquisition_mode = "api"

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self.typed_config = PledgeConfig.model_validate(config)
        self.client = PledgeAPIClient(self.typed_config)

    def validate_config(self) -> None:
        """Validate the Pledge source config."""
        self.typed_config = PledgeConfig.model_validate(self.config)
        self.client = PledgeAPIClient(self.typed_config)

    def test_connection(self) -> dict[str, Any]:
        """Issue a low-cost request against the donations endpoint."""
        payload = self.client.get(self.typed_config.donations_endpoint, params={"per": 1})
        return {
            "ok": True,
            "test_endpoint": self.typed_config.donations_endpoint,
            "total_count": payload.get("total_count"),
            "detected_keys": sorted(payload.keys()),
        }

    def list_supported_objects(self) -> list[str]:
        """Return supported Pledge object types."""
        return ["donations"]

    def fetch(self, request: FetchRequest) -> FetchResult:
        """Fetch requested Pledge donation objects."""
        items: list[RawFetchItem] = []
        object_types = request.object_types or self.typed_config.enabled_object_types
        for object_type in object_types:
            if object_type != "donations":
                continue
            items.extend(self._fetch_donations(request))
        cursor_time = (request.end_time or datetime.now(tz=UTC)).astimezone(UTC).isoformat()
        return FetchResult(
            items=items,
            cursor_state={"donations": {"last_end_time": cursor_time}},
            metadata={"fetched_object_types": object_types},
        )

    def normalize_raw_metadata(self, payload: dict[str, Any] | list[Any] | str) -> dict[str, Any]:
        """Extract lightweight metadata from a Pledge payload."""
        if not isinstance(payload, dict):
            return {"preview": str(payload)[:200]}
        organization = self._nested_dict(payload, "organization", "nonprofit", "charity")
        fundraiser = self._nested_dict(payload, "fundraiser", "campaign")
        return {
            "top_level_keys": sorted(payload.keys()),
            "organization_name": self._pick_nested(organization, "name"),
            "fundraiser_title": self._pick_nested(fundraiser, "title", "name"),
        }

    def extract_external_ids(self, payload: dict[str, Any] | list[Any] | str) -> dict[str, str | None]:
        """Extract Pledge record identifiers."""
        if not isinstance(payload, dict):
            return {"external_object_id": None, "external_parent_id": None}
        fundraiser = self._nested_dict(payload, "fundraiser", "campaign")
        external_object_id = self._pick(payload, "id", "donation_id", "charge_id", "uuid")
        external_parent_id = self._pick_nested(fundraiser, "id", "uuid")
        return {
            "external_object_id": str(external_object_id) if external_object_id else None,
            "external_parent_id": str(external_parent_id) if external_parent_id else None,
        }

    def _fetch_donations(self, request: FetchRequest) -> list[RawFetchItem]:
        items: list[RawFetchItem] = []
        page = 1
        previous_cursor = (request.cursor_state or {}).get("donations") or {}
        previous_end = self._parse_timestamp_value(previous_cursor.get("last_end_time"))
        next_url: str | None = None

        while True:
            payload = self.client.get(
                next_url or self.typed_config.donations_endpoint,
                params=None if next_url else {"page": page, "per": self.typed_config.page_size},
            )
            records = payload.get("results")
            if not isinstance(records, list):
                break
            dict_records = [record for record in records if isinstance(record, dict)]
            for record in dict_records:
                event_timestamp = self._parse_timestamp(record)
                if previous_end and event_timestamp and event_timestamp <= previous_end:
                    continue
                ids = self.extract_external_ids(record)
                items.append(
                    RawFetchItem(
                        object_type="donations",
                        external_object_id=ids["external_object_id"],
                        external_parent_id=ids["external_parent_id"],
                        payload=record,
                        event_timestamp=event_timestamp,
                        content_type="application/json",
                        source_channel="api",
                        metadata={"source_path": self.typed_config.donations_endpoint},
                    )
                )
            next_url = payload.get("next")
            if not next_url:
                break
            page += 1
        return items

    def _parse_timestamp(self, payload: dict[str, Any]) -> datetime | None:
        for key in (
            "created_at",
            "updated_at",
            "paid_at",
            "createdAt",
            "updatedAt",
            "paidAt",
            "donation_date",
            "donationDate",
        ):
            parsed = self._parse_timestamp_value(payload.get(key))
            if parsed is not None:
                return parsed
        return None

    def _parse_timestamp_value(self, value: Any) -> datetime | None:
        if not isinstance(value, str) or not value.strip():
            return None
        text = value.strip()
        for candidate in (text, text.replace("Z", "+00:00")):
            try:
                parsed = datetime.fromisoformat(candidate)
                if parsed.tzinfo is None:
                    return parsed.replace(tzinfo=UTC)
                return parsed.astimezone(UTC)
            except ValueError:
                continue
        return None

    def _pick(self, payload: dict[str, Any], *keys: str) -> Any:
        for key in keys:
            value = payload.get(key)
            if value not in (None, ""):
                return value
        return None

    def _pick_nested(self, payload: dict[str, Any], *keys: str) -> Any:
        if not isinstance(payload, dict):
            return None
        return self._pick(payload, *keys)

    def _nested_dict(self, payload: dict[str, Any], *keys: str) -> dict[str, Any]:
        for key in keys:
            value = payload.get(key)
            if isinstance(value, dict):
                return value
        return {}
