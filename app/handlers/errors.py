import logging

from aiogram import Router
from aiogram.types import ErrorEvent

router = Router()
logger = logging.getLogger(__name__)


@router.errors()
async def global_error_handler(event: ErrorEvent) -> bool:
    logger.exception("Unhandled bot exception: %s", event.exception)
    if event.update and event.update.message:
        await event.update.message.answer("Произошла ошибка. Попробуйте еще раз чуть позже.")
    return True
