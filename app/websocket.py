"""WebSocket endpoint for realtime event streaming.

Subscribes to Redis pub/sub channel ``project:<id>:events`` and forwards
every new Event record to connected WebSocket clients.  Also supports a
simple polling fallback via the REST ``/projects/{id}/events`` endpoint.
"""

from __future__ import annotations

import asyncio
import json
import uuid

import redis.asyncio as aioredis
import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config import settings

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.websocket("/ws/projects/{project_id}")
async def project_events_ws(websocket: WebSocket, project_id: uuid.UUID):
    await websocket.accept()
    logger.info("ws_connected", project_id=str(project_id))

    r = aioredis.from_url(settings.redis_url, decode_responses=True)
    pubsub = r.pubsub()
    channel = f"project:{project_id}:events"

    try:
        await pubsub.subscribe(channel)

        while True:
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if msg and msg["type"] == "message":
                await websocket.send_text(msg["data"])
            else:
                await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        logger.info("ws_disconnected", project_id=str(project_id))
    except Exception as exc:
        logger.error("ws_error", error=str(exc))
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()
        await r.close()
