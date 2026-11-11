"""add document storage key

Revision ID: a27f4b918d3c
Revises: 90086807fd85
Create Date: 2026-10-27 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a27f4b918d3c"
down_revision: Union[str, Sequence[str], None] = "90086807fd85"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("storage_key", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("documents", "storage_key")
