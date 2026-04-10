# Architecture Overview

## Purpose
The system is a single-organization ingestion backend that collects gift-source data, stores raw payloads, tracks ingestion runs, and exposes normalized records through a FastAPI API and lightweight operator UI.

## Main Components
- `app/main.py`: FastAPI application entrypoint.
- `app/api/`: API routing, dependencies, and operator-facing endpoints.
- `app/connectors/`: Source adapters such as OneCause, EveryOrg, Pledge, email, shared-folder, and portal-export.
- `app/connectors/registry.py`: Connector discovery and factory; new connector packages with a `connector.py` file are auto-discovered.
- `app/services/`: Coordination layer for source management, ingestion runs, raw object persistence, normalization, CSV imports, and scheduling.
- `app/services/ingestion_run_service.py`: Run lifecycle state transitions and run queries.
- `app/services/raw_item_ingestion_service.py`: Raw item storage, dedupe assignment, and normalization handoff.
- `app/models/`: SQLAlchemy models for sources, ingestion runs, raw objects, and normalized records.
- `app/schemas/`: Pydantic request and response models.
- `app/storage/filesystem.py`: Raw payload storage backend.
- `app/dedupe/service.py`: Duplicate detection and status assignment.
- `app/parsers/`: Metadata extraction for JSON, CSV, XLSX, PDF, and email payloads.
- `app/workers/job_runner.py`: In-process execution path for sync jobs.

## End-to-End Flow
1. A source is created through the API and stored as `SourceConfig`.
2. A connector is selected through `app/connectors/registry.py`.
3. The ingestion service triggers a fetch and creates an `IngestionRun`.
4. The connector returns raw fetch items with payloads and source metadata.
5. The storage layer writes raw payloads to `RAW_STORAGE_ROOT/...`.
6. `RawObject` rows capture lineage, metadata, and storage location.
7. Dedupe logic marks records as `unique`, `possible_duplicate`, or `confirmed_duplicate`.
8. Normalization services project raw data into canonical records such as `staging_gifts`.
9. API routes and the operator UI expose run status, raw objects, sources, and normalized outputs.

## Design Rules
- Keep connectors source-specific and side-effect light.
- Put workflow orchestration in services, not routes.
- Split run lifecycle from item persistence; avoid growing `IngestionService` into a catch-all.
- Preserve raw payloads as the source of truth.
- Flag duplicates rather than deleting data.
- Prefer configuration-driven connector behavior over hard-coded source assumptions.

## Adding a New Connector
1. Create `app/connectors/<source_name>/connector.py` with a `BaseConnector` subclass that sets `source_system` and `acquisition_mode`.
2. Add any source-specific client, schema, and config resolver code inside that package.
3. The registry will auto-discover the connector package; no central registry edit is required.
4. Keep source fetch logic inside the connector and let `IngestionService` reuse the shared run and persistence services.

## Operational Notes
Local development should use PostgreSQL plus filesystem raw storage. Migrations are managed with Alembic. The scheduler is in-process and intentionally simple, so future queue-based workers can replace it without changing connector contracts.
