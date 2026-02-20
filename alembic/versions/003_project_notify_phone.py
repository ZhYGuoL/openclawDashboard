"""Add notify_phone column to projects

Revision ID: 003
Revises: 002
Create Date: 2026-02-20
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("projects", sa.Column("notify_phone", sa.Text, nullable=True))


def downgrade() -> None:
    op.drop_column("projects", "notify_phone")
