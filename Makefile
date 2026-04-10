PYTHON ?= python3

.PHONY: install run test lint format migrate upgrade downgrade revision seed frontend-install frontend-dev frontend-build

install:
	$(PYTHON) -m pip install -e .[dev]

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest

lint:
	ruff check .

format:
	ruff format .

migrate:
	alembic upgrade head

upgrade:
	alembic upgrade head

downgrade:
	alembic downgrade -1

revision:
	alembic revision --autogenerate -m "$(m)"

seed:
	$(PYTHON) scripts/seed_onecause_source.py

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000 npm run dev

frontend-build:
	cd frontend && npm run build
