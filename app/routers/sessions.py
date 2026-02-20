from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Project, Thread
from app.schemas import SessionCreate, SessionRead
from app.workers.meeting import run_meeting_pipeline

router = APIRouter(tags=["sessions"])


@router.post("/projects/{project_id}/sessions", response_model=SessionRead, status_code=202)
async def start_session(
    project_id: uuid.UUID,
    body: SessionCreate,
    db: AsyncSession = Depends(get_db),
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    thread = Thread(project_id=project_id, title=body.thread_title)
    db.add(thread)
    await db.commit()
    await db.refresh(thread)

    task = run_meeting_pipeline.delay(
        str(project_id),
        str(thread.id),
        body.prompt,
    )

    return SessionRead(
        task_id=task.id,
        project_id=project_id,
        thread_id=thread.id,
        status="accepted",
    )
