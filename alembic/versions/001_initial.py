"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-02-19
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "agents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.Enum("pm", "engineer", "designer", "analyst", "memo_writer", name="agentrole"), nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("status", sa.Enum("idle", "running", "error", name="agentstatus"), server_default="idle"),
        sa.Column("config_json", JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "threads",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "messages",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("thread_id", UUID(as_uuid=True), sa.ForeignKey("threads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_type", sa.Enum("user", "agent", "system", name="authortype"), nullable=False),
        sa.Column("author_agent_id", UUID(as_uuid=True), nullable=True),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "decisions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("thread_id", UUID(as_uuid=True), sa.ForeignKey("threads.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("rationale", sa.Text, server_default=""),
        sa.Column("status", sa.Enum("proposed", "accepted", "rejected", name="decisionstatus"), server_default="proposed"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "action_items",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("owner_role", sa.Enum("pm", "engineer", "designer", "analyst", "memo_writer", name="agentrole", create_type=False), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("status", sa.Enum("open", "in_progress", "done", name="actionitemstatus"), server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "memos",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("content_markdown", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.Text, nullable=False),
        sa.Column("payload_json", JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_events_project_created", "events", ["project_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_events_project_created", table_name="events")
    op.drop_table("events")
    op.drop_table("memos")
    op.drop_table("action_items")
    op.drop_table("decisions")
    op.drop_table("messages")
    op.drop_table("threads")
    op.drop_table("agents")
    op.drop_table("projects")
    for enum_name in ("agentrole", "agentstatus", "authortype", "decisionstatus", "actionitemstatus"):
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
