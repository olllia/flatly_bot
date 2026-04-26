from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.keyboards.listing_form import main_menu_kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Этот бот сейчас работает только для сдачи жилья. Нажми кнопку ниже, чтобы создать объявление.",
        reply_markup=main_menu_kb(),
    )
