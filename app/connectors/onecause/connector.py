"""OneCause API connector."""

import json
from datetime import UTC, datetime
from typing import Any

from app.connectors.base.connector import BaseConnector
from app.connectors.base.types import FetchRequest, FetchResult, RawFetchItem
from app.connectors.onecause.client import OneCauseAPIClient
from app.connectors.onecause.schemas import OneCauseConfig


class OneCauseConnector(BaseConnector):
    """Production connector for OneCause API ingestion."""

    source_system = "onecause"
    acquisition_mode = "api"

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self.typed_config = OneCauseConfig.model_validate(config)
        self.client = OneCauseAPIClient(self.typed_config)

    def validate_config(self) -> None:
        """Validate the OneCause source config."""
        self.typed_config = OneCauseConfig.model_validate(self.config)

    def test_connection(self) -> dict[str, Any]:
        """Issue a low-cost request against the configured test endpoint."""
        endpoint = self.typed_config.test_endpoint.format(
            organization_id=self.typed_config.organization_id
        )
        params = {}
        if self.typed_config.auth_mode == "api_key":
            params = {
                self.typed_config.pagination_param_page: 1,
                self.typed_config.pagination_param_page_size: 1,
            }
        payload = self.client.get(endpoint, params)
        return {
            "ok": True,
            "test_endpoint": endpoint,
            "detected_keys": sorted(payload.keys()),
        }

    def list_supported_objects(self) -> list[str]:
        """Return supported OneCause object types."""
        return ["paid_activities", "supporters", "events", "fundraising_pages"]

    def fetch(self, request: FetchRequest) -> FetchResult:
        """Fetch requested OneCause objects, paginated and incremental-aware."""
        items: list[RawFetchItem] = []
        object_types = request.object_types or self.typed_config.enabled_object_types
        cursor_state = request.cursor_state or {}
        for object_type in object_types:
            items.extend(
                self._fetch_object_type(
                    object_type=object_type,
                    request=request,
                    previous_cursor=cursor_state.get(object_type),
                )
            )
        new_cursor = self._build_cursor_state(object_types, request.end_time)
        return FetchResult(
            items=items,
            cursor_state=new_cursor,
            metadata={"fetched_object_types": object_types},
        )

    def fetch_incremental(self, request: FetchRequest) -> FetchResult:
        """Run an incremental fetch."""
        return self.fetch(request)

    def fetch_paid_activities(self, request: FetchRequest) -> FetchResult:
        """Convenience method for paid activities sync."""
        request.object_types = ["paid_activities"]
        return self.fetch(request)

    def fetch_supporters(self, request: FetchRequest) -> FetchResult:
        """Convenience method for supporter sync."""
        request.object_types = ["supporters"]
        return self.fetch(request)

    def fetch_events(self, request: FetchRequest) -> FetchResult:
        """Convenience method for event sync."""
        request.object_types = ["events"]
        return self.fetch(request)

    def fetch_fundraising_pages(self, request: FetchRequest) -> FetchResult:
        """Convenience method for fundraising page sync."""
        request.object_types = ["fundraising_pages"]
        return self.fetch(request)

    def normalize_raw_metadata(self, payload: dict[str, Any] | list[Any] | str) -> dict[str, Any]:
        """Extract lightweight metadata from JSON responses."""
        if isinstance(payload, dict):
            return {"top_level_keys": sorted(payload.keys())}
        if isinstance(payload, list):
            return {"item_count": len(payload)}
        return {"preview": payload[:200]}

    def extract_external_ids(self, payload: dict[str, Any] | list[Any] | str) -> dict[str, str | None]:
        """Extract common OneCause IDs."""
        if isinstance(payload, dict):
            return {
                "external_object_id": str(payload.get("id")) if payload.get("id") is not None else None,
                "external_parent_id": str(payload.get("eventId"))
                if payload.get("eventId") is not None
                else None,
            }
        return {"external_object_id": None, "external_parent_id": None}

    def _fetch_object_type(
        self,
        object_type: str,
        request: FetchRequest,
        previous_cursor: dict[str, Any] | None,
    ) -> list[RawFetchItem]:
        endpoint_template = self.typed_config.endpoint_templates[object_type]
        endpoint = endpoint_template.format(organization_id=self.typed_config.organization_id)
        page = 1
        items: list[RawFetchItem] = []
        while True:
            params = self._build_params(
                object_type=object_type,
                page=page,
                request=request,
                previous_cursor=previous_cursor,
            )
            payload = self.client.get(endpoint, params=params)
            records = self._extract_records(object_type, payload)
            if not records:
                break
            for record in records:
                ids = self.extract_external_ids(record)
                items.append(
                    RawFetchItem(
                        object_type=object_type,
                        external_object_id=ids["external_object_id"],
                        external_parent_id=ids["external_parent_id"],
                        payload=record,
                        event_timestamp=self._parse_timestamp(record),
                        metadata=self.normalize_raw_metadata(record),
                    )
                )
            if not self._has_next_page(payload, page, len(records)):
                break
            page += 1
        return items

    def _build_params(
        self,
        object_type: str,
        page: int,
        request: FetchRequest,
        previous_cursor: dict[str, Any] | None,
    ) -> dict[str, Any]:
        if self.typed_config.auth_mode == "access_token":
            return self._build_portal_params(object_type=object_type, page=page)
        start_time = request.start_time
        if start_time is None and previous_cursor and previous_cursor.get("last_end_time"):
            start_time = datetime.fromisoformat(previous_cursor["last_end_time"])
        params: dict[str, Any] = {
            self.typed_config.pagination_param_page: page,
            self.typed_config.pagination_param_page_size: self.typed_config.page_size,
        }
        if start_time:
            params[self.typed_config.incremental_param_start] = start_time.astimezone(UTC).isoformat()
        if request.end_time:
            params[self.typed_config.incremental_param_end] = request.end_time.astimezone(UTC).isoformat()
        return params

    def _extract_records(self, object_type: str, payload: dict[str, Any] | list[Any]) -> list[dict[str, Any]]:
        if self.typed_config.auth_mode == "access_token":
            if isinstance(payload, list):
                return [item for item in payload if isinstance(item, dict)]
            if object_type == "events":
                for key in ("eventList", "events", "bidpalEventList", "bidpalEvents"):
                    value = payload.get(key)
                    if isinstance(value, list):
                        return [item for item in value if isinstance(item, dict)]
                return []
        list_key = self.typed_config.list_key_overrides.get(object_type)
        if list_key == "__root__" and isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if list_key and isinstance(payload.get(list_key), list):
            return payload[list_key]
        for key, value in payload.items():
            if isinstance(value, list):
                return value
        return []

    def _has_next_page(
        self,
        payload: dict[str, Any] | list[Any],
        current_page: int,
        record_count: int,
    ) -> bool:
        if self.typed_config.auth_mode == "access_token":
            return record_count >= self.typed_config.page_size and current_page == 1
        page_info = payload.get("pagination") or payload.get("page")
        if isinstance(page_info, dict):
            total_pages = page_info.get("total_pages") or page_info.get("totalPages")
            if total_pages:
                return current_page < int(total_pages)
            has_next = page_info.get("has_next") or page_info.get("hasNext")
            if has_next is not None:
                return bool(has_next)
        return record_count >= self.typed_config.page_size

    def _parse_timestamp(self, record: dict[str, Any]) -> datetime | None:
        for key in ("updatedAt", "createdAt", "paidAt", "timestamp", "completed", "modified", "created"):
            value = record.get(key)
            if isinstance(value, str):
                try:
                    return datetime.fromisoformat(value.replace("Z", "+00:00"))
                except ValueError:
                    continue
        return None

    def _build_cursor_state(
        self,
        object_types: list[str],
        end_time: datetime | None,
    ) -> dict[str, Any]:
        current_end = (end_time or datetime.now(tz=UTC)).astimezone(UTC).isoformat()
        return {object_type: {"last_end_time": current_end} for object_type in object_types}

    def _build_portal_params(self, object_type: str, page: int) -> dict[str, Any]:
        """Build query params for the portal access-token flow."""
        challenge_id = self.typed_config.challenge_id
        skip = max(page - 1, 0) * self.typed_config.page_size

        if object_type == "paid_activities":
            filter_payload = {
                "where": {
                    "status": {"inq": ["succeeded", "failed", "refunded"]},
                    "challengeId": challenge_id,
                },
                "include": [
                    {"relation": "participant", "scope": {"fields": ["name"]}},
                    {"relation": "teamParticipant", "scope": {"fields": ["name"]}},
                    {"relation": "team", "scope": {"fields": ["name"]}},
                ],
                "fields": [
                    "id",
                    "first_name",
                    "last_name",
                    "isCompanyDonation",
                    "companyName",
                    "email",
                    "fakeEmail",
                    "status",
                    "teamId",
                    "participantId",
                    "teamParticipantId",
                    "challengeId",
                    "charityId",
                    "completed",
                    "amount",
                    "donationRepeat",
                    "feesPaid",
                    "receiptNumber",
                ],
                "limit": min(self.typed_config.page_size, 500),
                "skip": skip,
                "order": ["completed DESC"],
            }
            return {"filter": json.dumps(filter_payload, separators=(",", ":"))}

        if object_type == "supporters":
            filter_payload = {
                "where": {"challengeId": challenge_id},
                "include": {"relation": "team", "scope": {"fields": ["name"]}},
                "fields": [
                    "id",
                    "userId",
                    "teamId",
                    "name",
                    "accepted",
                    "donationAmount",
                    "donationCount",
                    "teamCreditAmount",
                    "teamCreditCount",
                    "totalPointsEarned",
                    "eventId",
                    "eventIds",
                    "enableEmailFeature",
                    "adminOverrideEmailFeature",
                ],
                "limit": min(self.typed_config.page_size, 1000),
                "skip": skip,
                "order": ["name ASC"],
            }
            return {"filter": json.dumps(filter_payload, separators=(",", ":"))}

        if object_type == "fundraising_pages":
            filter_payload = {"where": {"challengeId": challenge_id}, "order": "name ASC"}
            return {"filter": json.dumps(filter_payload, separators=(",", ":"))}

        return {}
