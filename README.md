# Gift Ingestion Backend

Connector-first FastAPI backend for nonprofit gift-source ingestion. Phase 1 is focused on reliable data fetching, raw payload retention, ingestion run tracking, and duplicate-aware preprocessing for a single organization.

A small operator console is available at `/` for common source and sync actions, while Swagger remains available at `/docs`.

## Architecture

The project is intentionally modular and single-organization only:

- `app/api`: operator/developer-facing HTTP endpoints.
- `app/api/routes/ui.py`: lightweight operator console for manual workflows.
- `app/connectors`: pluggable ingestion connectors. OneCause, Pledge, Every.org, and Gmail are implemented; generic email, shared-folder, and portal-export remain scaffolded as first-class non-API patterns.
- `app/services`: orchestration and persistence services for sources, raw objects, and ingestion runs.
- `app/storage`: raw payload storage abstraction. Filesystem storage is the initial backend.
- `app/dedupe`: duplicate candidate detection that flags rather than deletes.
- `app/parsers`: lightweight metadata extraction hooks for JSON, CSV, XLSX, PDF, and email payloads.
- `app/workers`: simple synchronous job abstraction that can be replaced by Celery/RQ later.
- `app/models` and `app/schemas`: SQLAlchemy models and Pydantic request/response schemas.
- `alembic`: migrations.

The execution flow is:

1. Create a `SourceConfig`.
2. Test the connector configuration.
3. Trigger a sync.
4. Connector fetches raw source records and returns `RawFetchItem` values.
5. Raw payloads are stored on disk with a traceable path.
6. `RawObject` records persist payload lineage and metadata.
7. Dedupe service marks records as `unique`, `possible_duplicate`, or `confirmed_duplicate`.
8. `IngestionRun` stores counts, status, errors, and cursor state for future incremental runs.

## Project Layout

```text
app/
  api/
  connectors/
    base/
    email/
    gmail/
    onecause/
    portal_export/
    shared_folder/
  core/
  db/
  dedupe/
  models/
  parsers/
  schemas/
  services/
  storage/
  utils/
  workers/
alembic/
tests/
sample_data/
scripts/
```

## Setup

### Prerequisites

- Python 3.12+

PostgreSQL remains the intended production database, but the current local development setup in this workspace uses SQLite for a simpler manual run flow.

### Local Environment (Manual SQLite Setup)

1. Copy `.env.example` to `.env`.
2. For local manual development, set:
   - `DATABASE_URL=sqlite:///./gift_ingestion.db`
3. Set `RAW_STORAGE_ROOT`.
4. Install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

5. Run migrations:

```bash
alembic upgrade head
```

6. Start the API:

```bash
uvicorn app.main:app --reload
```

7. Open:

- UI: `http://localhost:8000/`
- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/api/v1/health`

### Local Environment (requirements.txt Alternative)

If another developer prefers not to install the project in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Docker Compose

`docker-compose.yml` is still included for teams that want containerized app + Postgres locally, but the simplest current handoff path is the manual SQLite setup above.

## Environment Variables

Defined in `.env.example`:

- `APP_ENV`
- `APP_NAME`
- `API_PREFIX`
- `DATABASE_URL`
- `RAW_STORAGE_ROOT`
- `LOG_LEVEL`
- `DEFAULT_REQUEST_TIMEOUT_SECONDS`
- `ONECAUSE_DEFAULT_BASE_URL`
- `ONECAUSE_API_BASE_URL`
- `ONECAUSE_API_KEY`
- `ONECAUSE_ORGANIZATION_ID`
- `ONECAUSE_CLIENT_ID`
- `ONECAUSE_ACCESS_TOKEN`
- `ONECAUSE_CHALLENGE_ID`
- `PLEDGE_API_BASE_URL`
- `PLEDGE_API_KEY`
- `GMAIL_API_BASE_URL`
- `GMAIL_USER_ID`
- `GMAIL_ACCESS_TOKEN`
- `GMAIL_REFRESH_TOKEN`
- `GMAIL_CLIENT_ID`
- `GMAIL_CLIENT_SECRET`
- `GMAIL_TOKEN_URL`
- `GMAIL_QUERY`
- `GMAIL_LABEL_IDS`
- `GMAIL_ATTACHMENT_MAX_BYTES`
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_GIFT_EXTRACTION_MODEL`
- `ENABLE_INPROCESS_SCHEDULER`
- `SCHEDULER_POLL_SECONDS`

Keep OneCause API secrets in environment variables or source configuration injected at runtime. Do not commit live credentials. If you maintain separate documentation-site credentials for the OneCause help center, keep those in local `.env` only; the app itself uses API credentials, not docs login credentials.

The app now resolves missing OneCause source config fields from `.env` during source creation and update. That means you can keep `ONECAUSE_API_BASE_URL`, `ONECAUSE_API_KEY`, and `ONECAUSE_ORGANIZATION_ID` in `.env` and send a minimal `config_json` when creating a OneCause source.
It also supports a portal-style fallback using `ONECAUSE_CLIENT_ID` plus `ONECAUSE_ACCESS_TOKEN` when you only have access to the authenticated client endpoints visible in the browser network tab.
For the live portal integration in this workspace, `ONECAUSE_CHALLENGE_ID` is also required because donations and participants are filtered by challenge.

## Migrations

```bash
alembic upgrade head
alembic downgrade -1
alembic revision --autogenerate -m "describe change"
```

## Development Commands

```bash
make install
make run
make test
make lint
make migrate
make seed
```

## Recommended Local Run Flow

This is the simplest local path for a new developer:

```bash
git clone <repo>
cd Gift
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
```

Then edit `.env` so it contains:

```env
DATABASE_URL=sqlite:///./gift_ingestion.db
RAW_STORAGE_ROOT=./raw_storage
```

Then run:

```bash
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Surface

Base prefix: `/api/v1`

- `GET /health`
- `POST /sources`
- `GET /sources`
- `GET /sources/{id}`
- `PATCH /sources/{id}`
- `POST /sources/{id}/test`
- `POST /sources/{id}/trigger`
- `GET /sources/{id}/ingestion-runs`
- `POST /sources/{id}/sync/onecause/paid-activities`
- `POST /sources/{id}/sync/onecause/supporters`
- `POST /sources/{id}/sync/onecause/full`
- `GET /ingestion-runs`
- `GET /ingestion-runs/{id}`
- `GET /raw-objects`
- `GET /raw-objects/{id}`
- `GET /raw-objects/{id}/payload`
- `POST /raw-objects/{id}/reprocess`
- `GET /normalized/records`
- `GET /normalized/gifts`
- `POST /scheduler/run-due`
- `GET /` operator console

Gmail uses the generic source lifecycle:

- `POST /sources/{id}/test`
- `POST /sources/{id}/trigger`
- `GET /sources/{id}/ingestion-runs`

Gmail extraction uses the OpenAI Responses API with structured JSON output. Supported attachments are uploaded as files and passed to the model; CSV, TSV, TXT, PDF, and XLSX can be analyzed with file inputs and Code Interpreter. Unsupported attachment types are still retained in raw storage for lineage.

## OneCause Configuration

The OneCause connector is implemented as an authenticated HTTP connector with configurable endpoint templates and explicit auth modes. This keeps the app usable even if your OneCause account’s exact resource paths or list keys differ from the defaults exposed in the help center.

Minimum config:

```json
{
  "api_base_url": "https://api.onecause.com",
  "api_key": "REPLACE_WITH_REAL_ONECAUSE_API_KEY",
  "organization_id": "REPLACE_WITH_ONECAUSE_ORG_ID"
}
```

If `ONECAUSE_API_BASE_URL`, `ONECAUSE_API_KEY`, and `ONECAUSE_ORGANIZATION_ID` are present in `.env`, you can create a OneCause source with a minimal payload such as:

```json
{
  "source_name": "OneCause Primary",
  "source_system": "onecause",
  "acquisition_mode": "api",
  "auth_type": "api_key",
  "enabled": true,
  "config_json": {}
}
```

Recommended config fields:

- `auth_mode`
- `api_base_url`
- `api_key`
- `organization_id`
- `client_id`
- `challenge_id`
- `page_size`
- `initial_sync_start`
- `enabled_object_types`
- `fetch_window_strategy`
- `timezone`
- `request_timeout_seconds`
- `auth_header_name`
- `test_endpoint`
- `endpoint_templates`
- `incremental_param_start`
- `incremental_param_end`
- `pagination_param_page`
- `pagination_param_page_size`
- `list_key_overrides`

Use `sample_data/onecause_source.seed.json` as the reference shape.

Because the official help article at `https://help.onecause.com/s/article/api-documentation` is login-gated, endpoint templates and top-level list keys are configurable in the source config instead of being frozen into the application.

If you are deriving values from browser network traffic during initial setup:

- `https://p2p.onecause.com/api/clients/<id>/...` indicates the client/org identifier.
- The `<id>` value can be used as `ONECAUSE_CLIENT_ID`.
- The active challenge id from the donations/participants requests can be used as `ONECAUSE_CHALLENGE_ID`.
- The `x-access-token` header can be used as `ONECAUSE_ACCESS_TOKEN`.
- Do not use the `cookie` header for backend auth.

Example from a browser request:

- Request URL: `https://p2p.onecause.com/api/clients/6706d23590dd062cef1357f5/admin-details`
- `ONECAUSE_CLIENT_ID=6706d23590dd062cef1357f5`
- `ONECAUSE_API_BASE_URL=https://p2p.onecause.com`
- `ONECAUSE_ACCESS_TOKEN=<value from x-access-token>`
- `ONECAUSE_CHALLENGE_ID=67338b7fb2c8096f058e0460`

This portal-token approach is useful when documented API credentials are not available, but it is inherently less stable than an official API key and may expire. Keep it as a fallback mode, not the preferred long-term connector design.

Preferred OneCause auth order:

1. `auth_mode=api_key` with a documented API key and organization id.
2. `auth_mode=access_token` with a persisted client id and refreshed access token.
3. Never use browser cookies as connector configuration.

## Canonical Normalized Model

Phase 1 persists a single canonical normalized record table for operator visibility:

- `staging_gifts` stores canonical normalized records across sources and object types
- `record_type` distinguishes rows such as `gift` and `supporter`
- `extra_metadata` captures source-specific spillover fields without forcing source-specific columns into the fixed model

The current fixed columns cover the common operating shape:

- source identifiers
- primary person name/email
- amount/currency/date
- campaign and related-entity attribution
- team, status, duplicate state, and reference values

Gmail normalization writes model-extracted gift rows into the same `staging_gifts` table, while raw email messages and attachments remain in `raw_objects` for lineage and reprocessing.

Raw payload retention remains the source of truth for lineage. The older `normalized_supporters` table and `/normalized/supporters` endpoint are kept only for compatibility while the UI and new integrations read from `/normalized/records`.

## Ingestion Runs

Each run is persisted in `ingestion_runs` and stores:

- run state transitions: `pending`, `running`, `completed`, `failed`
- record and duplicate counts
- cursor state for later incremental execution
- error messages
- connector metadata

The initial worker is synchronous and intentionally simple. You can later swap `app/workers/job_runner.py` with Celery, RQ, Dramatiq, or another queue without changing connector code or the API contract.

## Scheduling

For the current OneCause portal integration, use scheduled polling rather than webhooks.

Supported `schedule` values:

- `manual`
- `daily`
- `hourly`
- `every_6_hours`

When `ENABLE_INPROCESS_SCHEDULER=true`, the app runs a lightweight background scheduler and checks due sources every `SCHEDULER_POLL_SECONDS`.

## Raw Storage

Filesystem storage path format:

```text
RAW_STORAGE_ROOT / source_system / YYYY / MM / DD / run_<id> / object_type / <object_id>.json
```

This preserves raw lineage and keeps payload lookup traceable by source, date, run, object type, and object id.

## Dedupe Behavior

Duplicates are flagged, not dropped.

Current heuristics:

- exact payload checksum
- `source_system + external_object_id`
- filename plus timestamp heuristics

Statuses:

- `unique`
- `possible_duplicate`
- `confirmed_duplicate`

## Testing

Included tests cover:

- source creation
- source update
- connector validation
- OneCause connection testing with mocked HTTP responses
- OneCause fetch behavior with mocked paginated data
- Gmail mailbox polling, OpenAI-backed extraction, and normalized persistence
- dedupe detection

Run:

```bash
pytest
```

In the current workspace, syntax compilation passed. The test suite requires project dependencies to be installed first.

## Adding a New Connector

1. Create a new package under `app/connectors/<source_name>/`.
2. Implement `BaseConnector`.
3. Add typed config validation if the source has structured config.
4. Register the connector in `app/connectors/registry.py`.
5. Return `RawFetchItem` values only; keep source-specific mapping inside the connector package.
6. Reuse `IngestionService` for run tracking, raw storage, and dedupe.
7. Add tests with mocked source responses or sample files.

## Notes

- Single-organization only.
- No `tenant_id`.
- No SaaS tenant isolation.
- No AI classification, CRM posting, reviewer UI, or policy engine in this phase.
