PYTHON ?= python3

.PHONY: install run test lint format migrate upgrade downgrade revision seed

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

