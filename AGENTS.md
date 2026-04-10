# Repository Guidelines

## Project Structure
This repository is a connector-first FastAPI backend for nonprofit gift ingestion. Core application code lives in `app/`. Use `app/api` for HTTP routes and the operator UI, `app/connectors` for source-specific ingestion logic, `app/services` for orchestration, `app/models` and `app/schemas` for persistence and API contracts, and `app/storage`, `app/dedupe`, `app/parsers`, and `app/workers` for supporting pipeline behavior. Database migrations live in `alembic/`, tests in `tests/`, seed/sample files in `sample_data/` and `tests/fixtures/`, and utility scripts in `scripts/`.

## Architecture Reference
Read [docs/ARCHITECTURE.md](/home/saroj/Gift/docs/ARCHITECTURE.md) before changing ingestion flow, storage, dedupe, or normalization behavior. That document describes the end-to-end path from source configuration through connector fetch, raw-object persistence, normalization, and operator-facing APIs.

## Development Commands
Create a virtualenv with `python3 -m venv .venv` and activate it with `source .venv/bin/activate`. Install dependencies with `make install`. Start the app with `make run`. Apply migrations with `make migrate`. Run tests with `make test`, lint with `make lint`, and format with `make format`. Seed local OneCause config with `make seed`.

## Coding Standards
Target Python 3.12. Use 4-space indentation and keep lines within 100 characters. Follow the repo’s Ruff configuration for imports, bug-prone patterns, naming, and Python upgrades. Use `snake_case` for modules, functions, and variables; `PascalCase` for classes; and explicit source names for connector packages such as `app/connectors/onecause/` or `app/connectors/everyorg/`.

Keep boundaries clean:
- routes validate/request-response shaping
- services coordinate workflows
- connectors fetch and map source payloads
- models/schemas define storage and API contracts

Do not mix connector-specific fetch logic into API routes or unrelated services.

## Testing Standards
Use `pytest` for all tests. Name test files `test_<feature>.py` and keep shared fixtures in `tests/conftest.py` or `tests/fixtures/`. Add tests whenever you change connector behavior, normalization rules, dedupe logic, migrations, or API endpoints. Prefer mocked third-party responses over live external calls.

## Tools In Use
Primary tools in this repo:
- `FastAPI` for the API and operator UI entrypoint
- `SQLAlchemy` and `Alembic` for persistence and migrations
- `Pydantic` and `pydantic-settings` for schemas and config
- `httpx` for connector HTTP calls
- `pytest`, `pytest-asyncio`, and `pytest-cov` for testing
- `ruff` for linting and formatting
- `uvicorn` for local development server

## Commit & Pull Requests
Current git history uses short, lowercase summaries such as `added every org data fetch module`. Keep commits focused and concise. PRs should explain behavior changes, call out env or migration updates, link related issues, and include request samples or UI screenshots when changing operator-facing flows.

## Security & Config
Copy `.env.example` to `.env` and never commit live credentials. Keep `DATABASE_URL`, `RAW_STORAGE_ROOT`, and source-specific secrets valid for the local environment. Treat raw payloads and exported donation data as sensitive operational data.
