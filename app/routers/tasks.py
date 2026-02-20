from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Project, Task, TaskSource, TaskStatus
from app.schemas import TaskCreate, TaskDetailRead, TaskRead
from app.workers.executor import execute_task

router = APIRouter(tags=["tasks"])


@router.post("/projects/{project_id}/tasks", response_model=TaskRead, status_code=201)
async def create_task(
    project_id: uuid.UUID,
    body: TaskCreate,
    db: AsyncSession = Depends(get_db),
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    task = Task(
        project_id=project_id,
        agent_role=body.agent_role,
        title=body.title,
        description=body.description,
        task_type=body.task_type,
        status=TaskStatus.PENDING,
        source=TaskSource.DIRECT,
        workspace_dir=body.workspace_dir,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.get("/projects/{project_id}/tasks", response_model=list[TaskRead])
async def list_tasks(
    project_id: uuid.UUID,
    status: TaskStatus | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Task).where(Task.project_id == project_id)
    if status:
        query = query.where(Task.status == status)
    query = query.order_by(Task.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/tasks/{task_id}", response_model=TaskDetailRead)
async def get_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.artifacts))
        .where(Task.id == task_id)
    )
    task = result.scalars().first()
    if not task:
        raise HTTPException(404, "Task not found")
    return task


@router.post("/tasks/{task_id}/execute", response_model=dict, status_code=202)
async def trigger_execute(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    if task.status not in (TaskStatus.PENDING, TaskStatus.FAILED):
        raise HTTPException(
            409,
            f"Task is {task.status.value}; only pending or failed tasks can be executed",
        )

    celery_task = execute_task.delay(str(task_id))
    return {"task_id": str(task_id), "celery_task_id": celery_task.id, "status": "accepted"}
