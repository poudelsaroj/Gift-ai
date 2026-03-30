"""Seed a sample OneCause source config."""

from app.connectors.onecause.config_resolver import resolve_onecause_config
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.schemas.source import SourceConfigCreate
from app.services.source_service import SourceService


def main() -> None:
    settings = get_settings()
    payload = SourceConfigCreate(
        source_name="Sample OneCause Source",
        source_system="onecause",
        acquisition_mode="api",
        auth_type="api_key",
        config_json=resolve_onecause_config(
            {
                "initial_sync_start": "2026-01-01T00:00:00Z",
                "enabled_object_types": ["paid_activities", "supporters", "events"],
            },
            settings=settings,
        ),
        dedupe_keys=["external_object_id", "checksum_sha256"],
        notes="Seeded sample configuration for local development.",
    )
    with SessionLocal() as db:
        source = SourceService().create(db, payload)
        print(f"Created source {source.id}")


if __name__ == "__main__":
    main()
