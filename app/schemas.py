from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models import (
    ActionItemStatus,
    AgentRole,
    AgentStatus,
    AuthorType,
    DecisionStatus,
)


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------

class ProjectCreate(BaseModel):
    name: str


class ProjectRead(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class AgentCreate(BaseModel):
    role: AgentRole
    name: str
    config_json: dict[str, Any] = Field(default_factory=dict)


class AgentRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    role: AgentRole
    name: str
    status: AgentStatus
    config_json: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Thread
# ---------------------------------------------------------------------------

class ThreadCreate(BaseModel):
    title: str


class ThreadRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Message
# ---------------------------------------------------------------------------

class MessageCreate(BaseModel):
    content: str


class MessageRead(BaseModel):
    id: uuid.UUID
    thread_id: uuid.UUID
    author_type: AuthorType
    author_agent_id: uuid.UUID | None
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Session (kick off a meeting)
# ---------------------------------------------------------------------------

class SessionCreate(BaseModel):
    prompt: str = Field(..., description="User prompt / topic for the work session")
    thread_title: str = Field(default="Work Session", description="Title for the meeting thread")


class SessionRead(BaseModel):
    task_id: str
    project_id: uuid.UUID
    thread_id: uuid.UUID
    status: str


# ---------------------------------------------------------------------------
# Decision
# ---------------------------------------------------------------------------

class DecisionRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    thread_id: uuid.UUID | None
    title: str
    rationale: str
    status: DecisionStatus
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# ActionItem
# ---------------------------------------------------------------------------

class ActionItemRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    owner_role: AgentRole
    description: str
    status: ActionItemStatus
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Memo
# ---------------------------------------------------------------------------

class MemoRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    content_markdown: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Event
# ---------------------------------------------------------------------------

class EventRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    type: str
    payload_json: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}
