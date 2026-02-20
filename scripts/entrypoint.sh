#!/usr/bin/env bash
set -euo pipefail

case "${1:-api}" in
  api)
    echo "Running migrations..."
    alembic upgrade head
    echo "Starting API server..."
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ;;
  worker)
    echo "Starting Celery worker..."
    exec celery -A app.workers.celery_app worker --loglevel=info --concurrency=4
    ;;
  seed)
    exec python -m app.seed
    ;;
  *)
    exec "$@"
    ;;
esac
