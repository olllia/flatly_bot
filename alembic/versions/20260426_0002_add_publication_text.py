"""add publication text to listings

Revision ID: 20260426_0002
Revises: 20260426_0001
Create Date: 2026-04-26
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260426_0002"
down_revision: Union[str, None] = "20260426_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("listings", sa.Column("publication_text", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("listings", "publication_text")
