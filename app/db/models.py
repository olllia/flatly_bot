from datetime import datetime
from enum import Enum
from sqlalchemy import BIGINT, DateTime, Enum as SQLEnum, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class PropertyType(str, Enum):
    apartment = "apartment"
    room = "room"


class OwnerType(str, Enum):
    owner = "owner"
    subrent = "subrent"
    realtor = "realtor"


class ListingStatus(str, Enum):
    draft = "draft"
    moderation = "moderation"
    published = "published"
    rejected = "rejected"


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BIGINT, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False)
    property_type: Mapped[PropertyType | None] = mapped_column(
        SQLEnum(PropertyType, name="property_type_enum"),
        nullable=True,
    )
    owner_type: Mapped[OwnerType | None] = mapped_column(SQLEnum(OwnerType, name="owner_type_enum"), nullable=True)
    area: Mapped[float | None] = mapped_column(nullable=True)
    rooms: Mapped[float | None] = mapped_column(nullable=True)
    price: Mapped[int | None] = mapped_column(Integer, nullable=True)
    floor: Mapped[str | None] = mapped_column(String(50), nullable=True)
    metro: Mapped[str | None] = mapped_column(String(120), nullable=True)
    travel_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    travel_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    amenities: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    photos: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    status: Mapped[ListingStatus] = mapped_column(
        SQLEnum(ListingStatus, name="listing_status_enum"),
        default=ListingStatus.draft,
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
