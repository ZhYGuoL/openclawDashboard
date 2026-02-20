from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Message, AuthorType, Project, Thread
from app.schemas import MessageCreate, MessageRead, ThreadCreate, ThreadRead

router = APIRouter(tags=["threads"])


@router.post("/projects/{project_id}/threads", response_model=ThreadRead, status_code=201)
async def create_thread(
    project_id: uuid.UUID,
    body: ThreadCreate,
    db: AsyncSession = Depends(get_db),
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    thread = Thread(project_id=project_id, title=body.title)
    db.add(thread)
    await db.commit()
    await db.refresh(thread)
    return thread


@router.get("/threads/{thread_id}/messages", response_model=list[MessageRead])
async def list_messages(thread_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    thread = await db.get(Thread, thread_id)
    if not thread:
        raise HTTPException(404, "Thread not found")

    result = await db.execute(
        select(Message).where(Message.thread_id == thread_id).order_by(Message.created_at)
    )
    return result.scalars().all()


@router.post("/threads/{thread_id}/messages", response_model=MessageRead, status_code=201)
async def add_user_message(
    thread_id: uuid.UUID,
    body: MessageCreate,
    db: AsyncSession = Depends(get_db),
):
    thread = await db.get(Thread, thread_id)
    if not thread:
        raise HTTPException(404, "Thread not found")

    message = Message(
        thread_id=thread_id,
        author_type=AuthorType.USER,
        content=body.content,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message
