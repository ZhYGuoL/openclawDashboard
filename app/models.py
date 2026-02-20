from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum as _SAEnum, ForeignKey, Index, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _ValuesEnum(enum_cls: type) -> _SAEnum:
    """Create an SA Enum that uses the Python enum .value (lowercase) not .name (uppercase)."""
    return _SAEnum(enum_cls, values_callable=lambda e: [x.value for x in e])


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_id() -> uuid.UUID:
    return uuid.uuid4()


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AgentRole(str, enum.Enum):
    PM = "pm"
    ENGINEER = "engineer"
    DESIGNER = "designer"
    ANALYST = "analyst"
    MEMO_WRITER = "memo_writer"


class AgentStatus(str, enum.Enum):
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"


class AuthorType(str, enum.Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class DecisionStatus(str, enum.Enum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class ActionItemStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_new_id)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    agents: Mapped[list[Agent]] = relationship(back_populates="project", cascade="all, delete-orphan")
    threads: Mapped[list[Thread]] = relationship(back_populates="project", cascade="all, delete-orphan")
    decisions: Mapped[list[Decision]] = relationship(back_populates="project", cascade="all, delete-orphan")
    action_items: Mapped[list[ActionItem]] = relationship(back_populates="project", cascade="all, delete-orphan")
    memos: Mapped[list[Memo]] = relationship(back_populates="project", cascade="all, delete-orphan")
    events: Mapped[list[Event]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_new_id)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[AgentRole] = mapped_column(_ValuesEnum(AgentRole), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[AgentStatus] = mapped_column(_ValuesEnum(AgentStatus), default=AgentStatus.IDLE)
    config_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped[Project] = relationship(back_populates="agents")


class Thread(Base):
    __tablename__ = "threads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_new_id)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped[Project] = relationship(back_populates="threads")
    messages: Mapped[list[Message]] = relationship(back_populates="thread", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_new_id)
    thread_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("threads.id", ondelete="CASCADE"), nullable=False)
    author_type: Mapped[AuthorType] = mapped_column(_ValuesEnum(AuthorType), nullable=False)
    author_agent_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    thread: Mapped[Thread] = relationship(back_populates="messages")


class Decision(Base):
    __tablename__ = "decisions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_new_id)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    thread_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("threads.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[DecisionStatus] = mapped_column(_ValuesEnum(DecisionStatus), default=DecisionStatus.PROPOSED)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped[Project] = relationship(back_populates="decisions")


class ActionItem(Base):
    __tablename__ = "action_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_new_id)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    owner_role: Mapped[AgentRole] = mapped_column(_ValuesEnum(AgentRole), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ActionItemStatus] = mapped_column(_ValuesEnum(ActionItemStatus), default=ActionItemStatus.OPEN)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped[Project] = relationship(back_populates="action_items")


class Memo(Base):
    __tablename__ = "memos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_new_id)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    content_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped[Project] = relationship(back_populates="memos")


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        Index("ix_events_project_created", "project_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_new_id)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(Text, nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped[Project] = relationship(back_populates="events")
