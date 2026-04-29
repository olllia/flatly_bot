from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.keyboards.listing_form import main_menu_kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Это Flatly✨\n\n"
        "С помощью этого бота можно опубликовать объявление о сдаче жилья в нашем канале.\n\n"
        "Нажмите кнопку ниже, чтобы заполнить данные по вашей квартире. Это займет не больше пары минут.",
        reply_markup=main_menu_kb(),
    )
