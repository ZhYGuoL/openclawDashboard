from __future__ import annotations

from celery import Celery

from app.config import settings

celery = Celery(
    "openclaw_dashboard",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

celery.conf.update(include=["app.workers.meeting"])
