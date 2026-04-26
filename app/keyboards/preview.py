from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def preview_kb(listing_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Отправить на модерацию", callback_data=f"preview:submit:{listing_id}")
    builder.button(text="Изменить", callback_data=f"preview:edit:{listing_id}")
    builder.adjust(1)
    return builder.as_markup()


def moderation_kb_after_review(listing_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Опубликовать", callback_data=f"mod:publish:{listing_id}")
    builder.button(text="Редактировать", callback_data=f"mod:edittext:{listing_id}")
    builder.button(text="Запросить правки", callback_data=f"mod:requestchanges:{listing_id}")
    builder.button(text="Отклонить", callback_data=f"mod:reject:{listing_id}")
    builder.adjust(1)
    return builder.as_markup()


def moderation_kb_initial(listing_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Редактировать", callback_data=f"mod:edittext:{listing_id}")
    builder.button(text="Запросить правки", callback_data=f"mod:requestchanges:{listing_id}")
    builder.button(text="Отклонить", callback_data=f"mod:reject:{listing_id}")
    builder.button(text="Опубликовать", callback_data=f"mod:publish:{listing_id}")
    builder.adjust(1)
    return builder.as_markup()


EDITABLE_FIELDS = {
    "property_type": "Тип жилья",
    "owner_type": "Тип владельца",
    "area": "Площадь",
    "rooms": "Комнаты",
    "price": "Цена",
    "floor": "Этаж",
    "metro": "Метро",
    "travel_type": "Тип дороги",
    "travel_time": "Время до метро",
    "address": "Адрес",
    "description": "Описание",
    "amenities": "Удобства",
    "photos": "Фото",
}


def edit_fields_kb(listing_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, title in EDITABLE_FIELDS.items():
        builder.button(text=title, callback_data=f"editfield:{listing_id}:{key}")
    builder.button(text="Назад к превью", callback_data=f"editfield:{listing_id}:back")
    builder.adjust(2)
    return builder.as_markup()
