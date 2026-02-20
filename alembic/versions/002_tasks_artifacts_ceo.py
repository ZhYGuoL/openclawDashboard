"""Add tasks, artifacts tables and CEO role

Revision ID: 002
Revises: 001
Create Date: 2026-02-20
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID, ENUM as PG_ENUM

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Reference existing enum (do NOT recreate it)
agentrole = PG_ENUM(name="agentrole", create_type=False)

# New enum types created via raw SQL to avoid SQLAlchemy auto-creation issues
tasktype = PG_ENUM(name="tasktype", create_type=False)
taskstatus = PG_ENUM(name="taskstatus", create_type=False)
tasksource = PG_ENUM(name="tasksource", create_type=False)
artifacttype = PG_ENUM(name="artifacttype", create_type=False)


def upgrade() -> None:
    # Add 'ceo' to the existing agentrole enum
    op.execute("ALTER TYPE agentrole ADD VALUE IF NOT EXISTS 'ceo' BEFORE 'pm'")

    # New enum types via raw SQL (safe, idempotent)
    op.execute("DO $$ BEGIN CREATE TYPE tasktype AS ENUM ('code','design','research','review','analysis','document'); EXCEPTION WHEN duplicate_object THEN NULL; END $$")
    op.execute("DO $$ BEGIN CREATE TYPE taskstatus AS ENUM ('pending','running','completed','failed'); EXCEPTION WHEN duplicate_object THEN NULL; END $$")
    op.execute("DO $$ BEGIN CREATE TYPE tasksource AS ENUM ('meeting','direct'); EXCEPTION WHEN duplicate_object THEN NULL; END $$")
    op.execute("DO $$ BEGIN CREATE TYPE artifacttype AS ENUM ('file','commit','url','document','image'); EXCEPTION WHEN duplicate_object THEN NULL; END $$")

    op.create_table(
        "tasks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_role", agentrole, nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("task_type", tasktype, nullable=False),
        sa.Column("status", taskstatus, server_default="pending"),
        sa.Column("source", tasksource, server_default="direct"),
        sa.Column("action_item_id", UUID(as_uuid=True), sa.ForeignKey("action_items.id", ondelete="SET NULL"), nullable=True),
        sa.Column("result_summary", sa.Text, nullable=True),
        sa.Column("workspace_dir", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_tasks_project_status", "tasks", ["project_id", "status"])

    op.create_table(
        "artifacts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("task_id", UUID(as_uuid=True), sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("artifact_type", artifacttype, nullable=False),
        sa.Column("path_or_url", sa.Text, nullable=False),
        sa.Column("description", sa.Text, server_default=""),
        sa.Column("metadata_json", JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("artifacts")
    op.drop_index("ix_tasks_project_status", table_name="tasks")
    op.drop_table("tasks")
    for enum_name in ("tasktype", "taskstatus", "tasksource", "artifacttype"):
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
