from sqlalchemy import select

from app.db.models import Listing, ListingStatus
from app.db.session import SessionLocal


async def create_or_update_draft(user_id: int, username: str, payload: dict) -> Listing:
    async with SessionLocal() as session:
        stmt = (
            select(Listing)
            .where(Listing.user_id == user_id, Listing.status == ListingStatus.draft)
            .order_by(Listing.id.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        listing = result.scalar_one_or_none()

        if listing is None:
            listing = Listing(
                user_id=user_id,
                username=username,
                status=ListingStatus.draft,
            )
            session.add(listing)

        for key, value in payload.items():
            setattr(listing, key, value)

        await session.commit()
        await session.refresh(listing)
        return listing


async def get_listing_by_id(listing_id: int) -> Listing | None:
    async with SessionLocal() as session:
        result = await session.execute(select(Listing).where(Listing.id == listing_id))
        return result.scalar_one_or_none()


async def set_listing_status(listing_id: int, status: ListingStatus) -> Listing | None:
    async with SessionLocal() as session:
        result = await session.execute(select(Listing).where(Listing.id == listing_id))
        listing = result.scalar_one_or_none()
        if listing is None:
            return None
        listing.status = status
        await session.commit()
        await session.refresh(listing)
        return listing


async def update_listing_fields(listing_id: int, payload: dict) -> Listing | None:
    async with SessionLocal() as session:
        result = await session.execute(select(Listing).where(Listing.id == listing_id))
        listing = result.scalar_one_or_none()
        if listing is None:
            return None

        for key, value in payload.items():
            setattr(listing, key, value)

        listing.publication_text = None
        listing.publication_html = None
        listing.publication_entities = []
        listing.publication_photos = []
        listing.publication_source_chat_id = None
        listing.publication_source_message_id = None
        listing.status = ListingStatus.draft
        await session.commit()
        await session.refresh(listing)
        return listing


async def update_listing_admin_fields(listing_id: int, payload: dict) -> Listing | None:
    async with SessionLocal() as session:
        result = await session.execute(select(Listing).where(Listing.id == listing_id))
        listing = result.scalar_one_or_none()
        if listing is None:
            return None

        for key, value in payload.items():
            setattr(listing, key, value)

        await session.commit()
        await session.refresh(listing)
        return listing


async def get_moderation_listings(limit: int = 20) -> list[Listing]:
    async with SessionLocal() as session:
        result = await session.execute(
            select(Listing)
            .where(Listing.status == ListingStatus.moderation)
            .order_by(Listing.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
