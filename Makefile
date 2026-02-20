.PHONY: up down migrate seed api worker logs shell \
       local-setup local-deps local-db local-migrate local-api local-worker local-seed

# ──────────────────────────────────────────────
# Docker mode (requires Docker Desktop)
# ──────────────────────────────────────────────
up:
	cp -n .env.example .env 2>/dev/null || true
	docker compose up --build -d

down:
	docker compose down

migrate:
	docker compose exec api alembic upgrade head

seed:
	docker compose exec api python -m app.seed

logs:
	docker compose logs -f api worker

shell:
	docker compose exec api bash

# ──────────────────────────────────────────────
# Local mode (uses system Postgres 17 on macOS)
# ──────────────────────────────────────────────
local-deps:
	pip install -r requirements.txt

local-setup: local-deps
	cp -n .env.example .env 2>/dev/null || true
	@echo ""
	@echo "==> Next: run 'make local-db' (you will be prompted for the postgres superuser password)"
	@echo ""

local-db:
	@echo "This will prompt for the 'postgres' superuser password you set when Postgres 17 was installed."
	@echo "Creating role 'oclaw' and database 'openclaw_dashboard'..."
	/Library/PostgreSQL/17/bin/psql -h 127.0.0.1 -U postgres -c "DO \$$\$$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='oclaw') THEN CREATE ROLE oclaw LOGIN PASSWORD 'oclaw'; END IF; END \$$\$$;" 2>&1
	/Library/PostgreSQL/17/bin/psql -h 127.0.0.1 -U postgres -c "SELECT 'exists' FROM pg_database WHERE datname='openclaw_dashboard'" | grep -q exists || /Library/PostgreSQL/17/bin/psql -h 127.0.0.1 -U postgres -c "CREATE DATABASE openclaw_dashboard OWNER oclaw;"
	@echo ""
	@echo "Done. Now run: make local-migrate"

local-migrate:
	alembic upgrade head

local-api:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

local-worker:
	celery -A app.workers.celery_app worker --loglevel=info --concurrency=4

local-seed:
	python -m app.seed
