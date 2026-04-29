"""add publication source message to listings

Revision ID: 20260429_0004
Revises: 20260429_0003
Create Date: 2026-04-29
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260429_0004"
down_revision: Union[str, None] = "20260429_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("listings", sa.Column("publication_source_chat_id", sa.BIGINT(), nullable=True))
    op.add_column("listings", sa.Column("publication_source_message_id", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("listings", "publication_source_message_id")
    op.drop_column("listings", "publication_source_chat_id")
