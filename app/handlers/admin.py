from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.config import get_settings
from app.keyboards.preview import moderation_kb_initial
from app.services.listing_service import get_moderation_listings
from app.services.listing_text import format_listing_text, listing_to_text_payload

router = Router()
settings = get_settings()


@router.message(Command("moderation_queue"))
async def moderation_queue(message: Message) -> None:
    if not message.from_user or message.from_user.id != settings.admin_id:
        await message.answer("Команда доступна только администратору.")
        return

    listings = await get_moderation_listings(limit=20)
    if not listings:
        await message.answer("Очередь модерации пуста.")
        return

    await message.answer(f"Заявок в очереди: {len(listings)}")
    for listing in listings:
        payload = listing_to_text_payload(listing)
        text = format_listing_text(payload, username=listing.username)
        if listing.photos:
            await message.answer_photo(photo=listing.photos[0], caption=f"ID: {listing.id}\n\n{text}")
        else:
            await message.answer(f"ID: {listing.id}\n\n{text}")
        await message.answer("Действия модератора:", reply_markup=moderation_kb_initial(listing.id))
