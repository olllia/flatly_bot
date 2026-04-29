"""add publication html to listings

Revision ID: 20260429_0006
Revises: 20260429_0005
Create Date: 2026-04-29
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260429_0006"
down_revision: Union[str, None] = "20260429_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("listings", sa.Column("publication_html", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("listings", "publication_html")
