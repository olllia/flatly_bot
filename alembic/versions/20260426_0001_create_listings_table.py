"""create listings table

Revision ID: 20260426_0001
Revises:
Create Date: 2026-04-26
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260426_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

property_type_enum = sa.Enum("apartment", "room", name="property_type_enum")
owner_type_enum = sa.Enum("owner", "subrent", "realtor", name="owner_type_enum")
listing_status_enum = sa.Enum("draft", "moderation", "published", "rejected", name="listing_status_enum")


def upgrade() -> None:
    property_type_enum.create(op.get_bind(), checkfirst=True)
    owner_type_enum.create(op.get_bind(), checkfirst=True)
    listing_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "listings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BIGINT(), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("property_type", property_type_enum, nullable=True),
        sa.Column("owner_type", owner_type_enum, nullable=True),
        sa.Column("area", sa.Float(), nullable=True),
        sa.Column("rooms", sa.Float(), nullable=True),
        sa.Column("price", sa.Integer(), nullable=True),
        sa.Column("floor", sa.String(length=50), nullable=True),
        sa.Column("metro", sa.String(length=120), nullable=True),
        sa.Column("travel_type", sa.String(length=20), nullable=True),
        sa.Column("travel_time", sa.Integer(), nullable=True),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("amenities", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("photos", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("status", listing_status_enum, nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_listings_user_id", "listings", ["user_id"])
    op.create_index("ix_listings_status", "listings", ["status"])


def downgrade() -> None:
    op.drop_index("ix_listings_status", table_name="listings")
    op.drop_index("ix_listings_user_id", table_name="listings")
    op.drop_table("listings")
    listing_status_enum.drop(op.get_bind(), checkfirst=True)
    owner_type_enum.drop(op.get_bind(), checkfirst=True)
    property_type_enum.drop(op.get_bind(), checkfirst=True)
