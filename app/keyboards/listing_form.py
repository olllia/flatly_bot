from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

PROPERTY_TYPES = {
    "apartment": "Квартира",
    "room": "Комната",
}

OWNER_TYPES = {
    "owner": "Собственник",
    "subrent": "Субаренда",
    "realtor": "Риелтор",
}

TRAVEL_TYPES = {
    "Пешком": "walk",
    "Транспорт": "transport",
}

AMENITIES = [
    "Посудомойка",
    "Кондиционер",
    "Стиральная машина",
    "Интернет",
    "Мебель",
    "Телевизор",
    "Лифт",
    "С животными",
    "С детьми",
    "Мусоропровод",
    "Парковка",
    "Консьерж",
]

ROOM_OPTIONS = ["1", "2", "3", "4", "5", "6"]
TRAVEL_TIME_OPTIONS = ["3", "5", "7", "10", "15", "20"]


def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Создать объявление")]],
        resize_keyboard=True,
    )


def property_type_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=PROPERTY_TYPES["apartment"]), KeyboardButton(text=PROPERTY_TYPES["room"])],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def owner_type_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=OWNER_TYPES["owner"])],
            [KeyboardButton(text=OWNER_TYPES["subrent"])],
            [KeyboardButton(text=OWNER_TYPES["realtor"])],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def travel_type_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=k)] for k in TRAVEL_TYPES],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def amenities_kb(selected: set[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in AMENITIES:
        prefix = "✅ " if item in selected else ""
        builder.button(text=f"{prefix}{item}", callback_data=f"amenity:{item}")
    builder.adjust(2)
    builder.button(text="Готово", callback_data="amenity:done")
    return builder.as_markup()


def rooms_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=value) for value in ROOM_OPTIONS]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def travel_time_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=value) for value in TRAVEL_TIME_OPTIONS]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def photos_done_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Готово с фото", callback_data="photos:done")
    return builder.as_markup()
