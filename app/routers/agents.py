from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Agent, Project
from app.schemas import AgentCreate, AgentRead

router = APIRouter(tags=["agents"])


@router.post("/projects/{project_id}/agents", response_model=AgentRead, status_code=201)
async def create_agent(
    project_id: uuid.UUID,
    body: AgentCreate,
    db: AsyncSession = Depends(get_db),
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    agent = Agent(
        project_id=project_id,
        role=body.role,
        name=body.name,
        config_json=body.config_json,
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent


@router.get("/projects/{project_id}/agents", response_model=list[AgentRead])
async def list_agents(project_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Agent).where(Agent.project_id == project_id).order_by(Agent.created_at)
    )
    return result.scalars().all()
