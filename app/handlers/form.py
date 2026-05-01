import logging
import socket

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, InputMediaPhoto, Message, ReplyKeyboardRemove
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.db.models import Listing, ListingStatus
from app.keyboards.listing_form import (
    OWNER_TYPES,
    PROPERTY_TYPES,
    ROOM_OPTIONS,
    TRAVEL_TYPES,
    TRAVEL_TIME_OPTIONS,
    amenities_kb,
    photos_done_kb,
    owner_type_kb,
    property_type_kb,
    rooms_kb,
    travel_time_kb,
    travel_type_kb,
)
from app.keyboards.preview import EDITABLE_FIELDS, edit_fields_kb, moderation_kb_initial, preview_kb
from app.services.listing_service import (
    create_or_update_draft,
    get_listing_by_id,
    set_listing_status,
    update_listing_fields,
)
from app.services.listing_text import format_listing_text, listing_to_text_payload
from app.states.listing_form import ListingForm
from app.utils.validators import to_positive_int, to_positive_number

router = Router()
logger = logging.getLogger(__name__)
settings = get_settings()


def _target_publication_chat_id() -> int:
    return settings.draft_channel_id


@router.message(Command("new"))
async def start_listing_form(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(ListingForm.property_type)
    await state.update_data(amenities=[], photos=[])
    await message.answer("Выберите тип жилья:", reply_markup=property_type_kb())


@router.message(F.text == "Создать объявление")
async def start_listing_form_button(message: Message, state: FSMContext) -> None:
    await start_listing_form(message, state)


async def _send_preview(chat_message: Message, listing: Listing) -> None:
    payload = listing_to_text_payload(listing)
    preview_text = format_listing_text(payload, username=listing.username)
    photos = listing.photos or []
    if photos:
        media = [InputMediaPhoto(media=file_id) for file_id in photos]
        await chat_message.answer_media_group(media=media)
    await chat_message.answer(preview_text, reply_markup=preview_kb(listing.id))


def _validate_edit_value(field: str, raw: str):
    text = raw.strip()
    if field == "price":
        value = to_positive_int(text)
        return (value, "Цена должна быть целым положительным числом.") if value else (None, "Цена должна быть целым положительным числом.")
    if field == "description":
        if not text:
            return None, "Описание не должно быть пустым."
        if len(text) > 350:
            return None, "Описание должно быть до 350 символов."
        return text, None
    if field == "metro":
        if not text or len(text) > 120:
            return None, "Метро должно быть от 1 до 120 символов."
        return text, None
    if field == "address":
        if not text or len(text) > 255:
            return None, "Адрес должен быть от 1 до 255 символов."
        return text, None
    if field == "floor":
        if not text or len(text) > 50:
            return None, "Этаж должен быть от 1 до 50 символов."
        return text, None
    if field in ("area", "rooms"):
        value = to_positive_number(text)
        if value is None:
            return None, "Введите положительное число."
        return value, None
    if field == "travel_time":
        value = to_positive_int(text)
        if value is None or value > 180:
            return None, "Введите целое число от 1 до 180."
        return value, None
    if field == "property_type":
        if text not in PROPERTY_TYPES:
            return None, "Допустимо: apartment или room."
        return text, None
    if field == "owner_type":
        if text not in OWNER_TYPES:
            return None, "Допустимо: owner, subrent, realtor."
        return text, None
    if field == "travel_type":
        if text not in ("walk", "transport"):
            return None, "Допустимо: walk или transport."
        return text, None
    if field == "amenities":
        items = [item.strip() for item in text.split(",") if item.strip()]
        return items, None
    return None, "Это поле нельзя изменить через текст."


@router.message(ListingForm.property_type)
async def handle_property_type(message: Message, state: FSMContext) -> None:
    reverse = {v: k for k, v in PROPERTY_TYPES.items()}
    value = reverse.get((message.text or "").strip())
    if not value:
        await message.answer("Выберите тип жилья кнопкой ниже.", reply_markup=property_type_kb())
        return
    await state.update_data(property_type=value)
    await state.set_state(ListingForm.owner_type)
    await message.answer("Кто вы?", reply_markup=owner_type_kb())


@router.message(ListingForm.owner_type)
async def handle_owner_type(message: Message, state: FSMContext) -> None:
    reverse = {v: k for k, v in OWNER_TYPES.items()}
    value = reverse.get((message.text or "").strip())
    if not value:
        await message.answer("Выберите вариант кнопкой.", reply_markup=owner_type_kb())
        return
    await state.update_data(owner_type=value)
    await state.set_state(ListingForm.area)
    await message.answer("Площадь (м2), например 42.5:", reply_markup=ReplyKeyboardRemove())


@router.message(ListingForm.area)
async def handle_area(message: Message, state: FSMContext) -> None:
    value = to_positive_number(message.text or "")
    if value is None:
        await message.answer("Введите корректную площадь, например 38 или 38.5.")
        return
    await state.update_data(area=value)
    await state.set_state(ListingForm.rooms)
    await message.answer("Количество комнат:", reply_markup=rooms_kb())


@router.message(ListingForm.rooms)
async def handle_rooms(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    if raw not in ROOM_OPTIONS:
        await message.answer("Выберите количество комнат кнопкой.", reply_markup=rooms_kb())
        return
    await state.update_data(rooms=int(raw))
    await state.set_state(ListingForm.price)
    await message.answer("Цена в рублях/месяц, только число:", reply_markup=ReplyKeyboardRemove())


@router.message(ListingForm.price)
async def handle_price(message: Message, state: FSMContext) -> None:
    value = to_positive_int(message.text or "")
    if value is None:
        await message.answer("Введите корректную цену, например 65000.")
        return
    await state.update_data(price=value)
    await state.set_state(ListingForm.floor)
    await message.answer("Этаж (например: 5/16):")


@router.message(ListingForm.floor)
async def handle_floor(message: Message, state: FSMContext) -> None:
    value = (message.text or "").strip()
    if not value or len(value) > 50:
        await message.answer("Введите этаж в формате до 50 символов, например 5/16.")
        return
    await state.update_data(floor=value)
    await state.set_state(ListingForm.metro)
    await message.answer("Ближайшее метро:")


@router.message(ListingForm.metro)
async def handle_metro(message: Message, state: FSMContext) -> None:
    value = (message.text or "").strip()
    if not value or len(value) > 120:
        await message.answer("Введите название метро (до 120 символов).")
        return
    await state.update_data(metro=value)
    await state.set_state(ListingForm.travel_type)
    await message.answer("Как добираться до метро?", reply_markup=travel_type_kb())


@router.message(ListingForm.travel_type)
async def handle_travel_type(message: Message, state: FSMContext) -> None:
    value = TRAVEL_TYPES.get((message.text or "").strip())
    if not value:
        await message.answer("Выберите вариант кнопкой.", reply_markup=travel_type_kb())
        return
    await state.update_data(travel_type=value)
    await state.set_state(ListingForm.travel_time)
    await message.answer("Сколько минут до метро?", reply_markup=travel_time_kb())


@router.message(ListingForm.travel_time)
async def handle_travel_time(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    if raw not in TRAVEL_TIME_OPTIONS:
        await message.answer("Выберите время кнопкой.", reply_markup=travel_time_kb())
        return
    value = int(raw)
    await state.update_data(travel_time=value)
    await state.set_state(ListingForm.address)
    await message.answer("Введите адрес:", reply_markup=ReplyKeyboardRemove())


@router.message(ListingForm.address)
async def handle_address(message: Message, state: FSMContext) -> None:
    value = (message.text or "").strip()
    if not value or len(value) > 255:
        await message.answer("Введите адрес до 255 символов.")
        return
    await state.update_data(address=value)
    await state.set_state(ListingForm.amenities)
    await message.answer("Выберите удобства (можно несколько):", reply_markup=amenities_kb(set()))


@router.callback_query(ListingForm.amenities, F.data.startswith("amenity:"))
async def handle_amenities(callback: CallbackQuery, state: FSMContext) -> None:
    raw = callback.data.split(":", maxsplit=1)[1]
    data = await state.get_data()
    selected = set(data.get("amenities", []))

    if raw == "done":
        await state.update_data(amenities=sorted(selected))
        await state.set_state(ListingForm.description)
        await callback.message.answer("Введите описание (до 350 символов):")
        await callback.answer()
        return

    if raw in selected:
        selected.remove(raw)
    else:
        selected.add(raw)

    await state.update_data(amenities=sorted(selected))
    await callback.message.edit_reply_markup(reply_markup=amenities_kb(selected))
    await callback.answer()


@router.message(ListingForm.description)
async def handle_description(message: Message, state: FSMContext) -> None:
    value = (message.text or "").strip()
    if not value:
        await message.answer("Описание не должно быть пустым.")
        return
    if len(value) > 350:
        await message.answer(f"Слишком длинно: {len(value)} символов. Максимум 350.")
        return
    await state.update_data(description=value)
    await state.set_state(ListingForm.photos)
    await message.answer(
        "Отправьте до 6 фото. Когда закончите, нажмите кнопку «Готово с фото».",
        reply_markup=ReplyKeyboardRemove(),
    )
    await message.answer("Завершение загрузки:", reply_markup=photos_done_kb())


async def _finalize_draft(message: Message, state: FSMContext, user_id: int, username: str) -> None:
    data = await state.get_data()
    photos: list[str] = data.get("photos", [])
    if not photos:
        await message.answer("Нужно добавить хотя бы 1 фото.")
        return

    payload = {
        "property_type": data["property_type"],
        "owner_type": data["owner_type"],
        "area": data["area"],
        "rooms": data["rooms"],
        "price": data["price"],
        "floor": data["floor"],
        "metro": data["metro"],
        "travel_type": data["travel_type"],
        "travel_time": data["travel_time"],
        "address": data["address"],
        "description": data["description"],
        "amenities": data.get("amenities", []),
        "photos": photos,
    }

    listing = await create_or_update_draft(
        user_id=user_id,
        username=username,
        payload=payload,
    )
    await _send_preview(message, listing)
    await state.clear()
    logger.info("Draft listing %s generated by user=%s", listing.id, user_id)


@router.callback_query(ListingForm.photos, F.data == "photos:done")
async def done_photos_cb(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.message or not callback.from_user:
        await callback.answer()
        return
    username = callback.from_user.username or f"id{callback.from_user.id}"
    try:
        await _finalize_draft(callback.message, state, callback.from_user.id, username)
    except (SQLAlchemyError, OSError, socket.gaierror):
        await callback.message.answer(
            "Не удалось сохранить объявление: нет подключения к базе данных. "
            "Проверьте DATABASE_URL в .env и что Postgres запущен."
        )
        await callback.answer("Ошибка БД", show_alert=True)
        return
    await callback.answer("Черновик сохранен")


@router.message(ListingForm.photos, F.photo)
async def add_photo(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    photos: list[str] = data.get("photos", [])
    if len(photos) >= 6:
        await message.answer("Уже загружено 6 фото. Нажмите кнопку «Готово с фото».")
        return

    file_id = message.photo[-1].file_id
    photos.append(file_id)
    await state.update_data(photos=photos)
    await message.answer(f"Фото добавлено ({len(photos)}/6).")


@router.message(ListingForm.photos)
async def photos_only(message: Message) -> None:
    await message.answer("Отправьте фото или нажмите кнопку «Готово с фото».")


@router.callback_query(F.data.startswith("preview:"))
async def preview_actions(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    if not callback.data:
        await callback.answer()
        return
    _, action, listing_id_raw = callback.data.split(":")
    listing_id = int(listing_id_raw)
    listing = await get_listing_by_id(listing_id)
    if not listing:
        await callback.answer("Объявление не найдено.", show_alert=True)
        return

    if not callback.from_user or listing.user_id != callback.from_user.id:
        await callback.answer("Недостаточно прав.", show_alert=True)
        return

    if action == "submit":
        listing = await set_listing_status(listing_id, ListingStatus.moderation)
        if not listing:
            await callback.answer("Не удалось отправить на модерацию.", show_alert=True)
            return
        payload = listing_to_text_payload(listing)
        text = format_listing_text(payload, username=listing.username)
        photos = listing.photos or []
        if photos:
            media = [InputMediaPhoto(media=file_id) for file_id in photos]
            await bot.send_media_group(chat_id=settings.admin_id, media=media)
        await bot.send_message(
            chat_id=settings.admin_id,
            text=f"Новая заявка на модерацию (ID: {listing.id})\n\n{text}",
            reply_markup=moderation_kb_initial(listing.id),
        )
        await callback.message.answer("Отправлено на модерацию.")
        await callback.answer("Готово")
        return
    if action == "edit":
        await callback.message.answer(
            f"Выберите поле для редактирования (ID: {listing.id}):",
            reply_markup=edit_fields_kb(listing.id),
        )
        await callback.answer()
        return
    await callback.answer()


@router.callback_query(F.data.startswith("mod:"))
async def moderation_actions(callback: CallbackQuery, bot: Bot) -> None:
    if not callback.data:
        await callback.answer()
        return
    if not callback.from_user or callback.from_user.id != settings.admin_id:
        await callback.answer("Только для администратора.", show_alert=True)
        return

    _, action, listing_id_raw = callback.data.split(":")
    listing_id = int(listing_id_raw)
    listing = await get_listing_by_id(listing_id)
    if not listing:
        await callback.answer("Объявление не найдено.", show_alert=True)
        return

    if action == "publish":
        payload = listing_to_text_payload(listing)
        text = format_listing_text(payload, username=listing.username)
        photos = listing.photos or []
        target_chat_id = _target_publication_chat_id()
        try:
            if photos:
                first_media = InputMediaPhoto(media=photos[0], caption=text, parse_mode="HTML")
                media = [first_media]
                media.extend(InputMediaPhoto(media=file_id) for file_id in photos[1:])
                await bot.send_media_group(chat_id=target_chat_id, media=media)
            else:
                await bot.send_message(chat_id=target_chat_id, text=text, parse_mode="HTML")
            await set_listing_status(listing_id, ListingStatus.published)
            await bot.send_message(
                chat_id=listing.user_id,
                text="Ваше объявление отправлено в канал-черновик и ожидает ручной публикации администратором.",
            )
            logger.info("Listing %s published to draft channel %s", listing_id, target_chat_id)
            await callback.answer("Отправлено в черновик")
        except TelegramAPIError:
            logger.exception("Failed to publish listing %s to draft channel %s", listing_id, target_chat_id)
            await callback.message.answer(
                "Не удалось отправить объявление в канал-черновик. Проверьте, что бот добавлен в канал и имеет право публиковать сообщения."
            )
            await callback.answer("Ошибка публикации", show_alert=True)
        return

    if action == "reject":
        await set_listing_status(listing_id, ListingStatus.rejected)
        await bot.send_message(chat_id=listing.user_id, text="Объявление отклонено модератором.")
        await callback.answer("Отклонено")
        return

    if action == "requestchanges":
        await set_listing_status(listing_id, ListingStatus.draft)
        await bot.send_message(
            chat_id=listing.user_id,
            text=f"Модератор запросил правки по объявлению ID {listing.id}. Выберите поле для исправления:",
            reply_markup=edit_fields_kb(listing.id),
        )
        await callback.answer("Пользователь уведомлен")
        return

    await callback.answer()


@router.callback_query(F.data.startswith("editfield:"))
async def edit_field_selector(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data:
        await callback.answer()
        return
    _, listing_id_raw, field = callback.data.split(":")
    listing_id = int(listing_id_raw)
    listing = await get_listing_by_id(listing_id)
    if not listing:
        await callback.answer("Объявление не найдено.", show_alert=True)
        return
    if not callback.from_user or callback.from_user.id != listing.user_id:
        await callback.answer("Недостаточно прав.", show_alert=True)
        return

    if field == "back":
        await _send_preview(callback.message, listing)
        await callback.answer()
        return

    if field not in EDITABLE_FIELDS:
        await callback.answer("Неизвестное поле.", show_alert=True)
        return

    if field == "photos":
        await state.set_state(ListingForm.edit_photos)
        await state.update_data(edit_listing_id=listing_id, edit_field=field, photos=[])
        await callback.message.answer("Отправьте новые фото (до 6), затем нажмите кнопку «Готово с фото».")
        await callback.message.answer("Завершение загрузки:", reply_markup=photos_done_kb())
        await callback.answer()
        return

    await state.set_state(ListingForm.edit_value)
    await state.update_data(edit_listing_id=listing_id, edit_field=field)
    await callback.message.answer(f"Введите новое значение для поля: {EDITABLE_FIELDS[field]}")
    await callback.answer()


@router.message(ListingForm.edit_value)
async def edit_field_value(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    listing_id = data.get("edit_listing_id")
    field = data.get("edit_field")
    if not listing_id or not field:
        await state.clear()
        await message.answer("Сессия редактирования устарела. Откройте редактирование снова.")
        return

    listing = await get_listing_by_id(int(listing_id))
    if not listing or not message.from_user or listing.user_id != message.from_user.id:
        await state.clear()
        await message.answer("Объявление недоступно.")
        return

    value, error = _validate_edit_value(field, message.text or "")
    if error:
        await message.answer(error)
        return

    updated = await update_listing_fields(listing.id, {field: value})
    if not updated:
        await message.answer("Не удалось сохранить изменения.")
        return

    await message.answer("Изменения сохранены. Обновленное превью:")
    await _send_preview(message, updated)
    await state.clear()


@router.message(ListingForm.edit_photos, F.photo)
async def edit_listing_photos(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    photos: list[str] = data.get("photos", [])
    if len(photos) >= 6:
        await message.answer("Достигнут лимит 6 фото. Нажмите кнопку «Готово с фото».")
        return
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    await message.answer(f"Фото добавлено ({len(photos)}/6).")


async def _done_edit_listing_photos(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    listing_id = data.get("edit_listing_id")
    photos: list[str] = data.get("photos", [])
    if not listing_id:
        await state.clear()
        await message.answer("Сессия редактирования устарела.")
        return
    if not photos:
        await message.answer("Добавьте хотя бы одно фото.")
        return

    listing = await get_listing_by_id(int(listing_id))
    if not listing or not message.from_user or listing.user_id != message.from_user.id:
        await state.clear()
        await message.answer("Объявление недоступно.")
        return

    updated = await update_listing_fields(listing.id, {"photos": photos})
    if not updated:
        await message.answer("Не удалось обновить фото.")
        return

    await message.answer("Фото обновлены. Обновленное превью:")
    await _send_preview(message, updated)
    await state.clear()


@router.callback_query(ListingForm.edit_photos, F.data == "photos:done")
async def done_edit_listing_photos_cb(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.message:
        await callback.answer()
        return
    try:
        await _done_edit_listing_photos(callback.message, state)
    except (SQLAlchemyError, OSError, socket.gaierror):
        await callback.message.answer(
            "Не удалось обновить фото: нет подключения к базе данных. "
            "Проверьте DATABASE_URL в .env и что Postgres запущен."
        )
        await callback.answer("Ошибка БД", show_alert=True)
        return
    await callback.answer("Фото обновлены")


@router.message(ListingForm.edit_photos)
async def edit_photos_only(message: Message) -> None:
    await message.answer("Отправьте фото или нажмите кнопку «Готово с фото».")
