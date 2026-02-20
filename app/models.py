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
    CEO = "ceo"
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


class TaskType(str, enum.Enum):
    CODE = "code"
    DESIGN = "design"
    RESEARCH = "research"
    REVIEW = "review"
    ANALYSIS = "analysis"
    DOCUMENT = "document"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskSource(str, enum.Enum):
    MEETING = "meeting"
    DIRECT = "direct"


class ArtifactType(str, enum.Enum):
    FILE = "file"
    COMMIT = "commit"
    URL = "url"
    DOCUMENT = "document"
    IMAGE = "image"


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_new_id)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    notify_phone: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    agents: Mapped[list[Agent]] = relationship(back_populates="project", cascade="all, delete-orphan")
    threads: Mapped[list[Thread]] = relationship(back_populates="project", cascade="all, delete-orphan")
    decisions: Mapped[list[Decision]] = relationship(back_populates="project", cascade="all, delete-orphan")
    action_items: Mapped[list[ActionItem]] = relationship(back_populates="project", cascade="all, delete-orphan")
    memos: Mapped[list[Memo]] = relationship(back_populates="project", cascade="all, delete-orphan")
    events: Mapped[list[Event]] = relationship(back_populates="project", cascade="all, delete-orphan")
    tasks: Mapped[list[Task]] = relationship(back_populates="project", cascade="all, delete-orphan")
    artifacts: Mapped[list[Artifact]] = relationship(back_populates="project", cascade="all, delete-orphan")


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


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        Index("ix_tasks_project_status", "project_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_new_id)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    agent_role: Mapped[AgentRole] = mapped_column(_ValuesEnum(AgentRole), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    task_type: Mapped[TaskType] = mapped_column(_ValuesEnum(TaskType), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(_ValuesEnum(TaskStatus), default=TaskStatus.PENDING)
    source: Mapped[TaskSource] = mapped_column(_ValuesEnum(TaskSource), default=TaskSource.DIRECT)
    action_item_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("action_items.id", ondelete="SET NULL"), nullable=True,
    )
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    workspace_dir: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped[Project] = relationship(back_populates="tasks")
    artifacts: Mapped[list[Artifact]] = relationship(back_populates="task", cascade="all, delete-orphan")


class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_new_id)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    artifact_type: Mapped[ArtifactType] = mapped_column(_ValuesEnum(ArtifactType), nullable=False)
    path_or_url: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped[Project] = relationship(back_populates="artifacts")
    task: Mapped[Task] = relationship(back_populates="artifacts")
