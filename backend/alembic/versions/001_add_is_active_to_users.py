"""add is_active to users

Revision ID: 001
Revises:
Create Date: 2026-08-06
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )


def downgrade() -> None:
    op.drop_column("users", "is_active")
