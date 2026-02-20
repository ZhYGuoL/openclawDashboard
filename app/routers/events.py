from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Event
from app.schemas import EventRead

router = APIRouter(tags=["events"])


@router.get("/projects/{project_id}/events", response_model=list[EventRead])
async def list_events(
    project_id: uuid.UUID,
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Event)
        .where(Event.project_id == project_id)
        .order_by(Event.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()
