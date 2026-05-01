import html

from app.keyboards.listing_form import AMENITIES, OWNER_TYPES, PROPERTY_TYPES

TRAVEL_TYPES_RU = {
    "walk": "пешком",
    "transport": "на транспорте",
}


def _price_tag(price_value: int) -> str:
    if price_value <= 0:
        return "#цена"
    price_bucket = max(10, ((price_value + 9999) // 10000) * 10)
    return f"#до{price_bucket}"


def _format_number(value: float | int | None) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _format_price(value: int | None) -> str:
    if value is None:
        return ""
    return f"{value:,}".replace(",", " ")


def format_listing_text(data: dict, username: str) -> str:
    property_type = html.escape(PROPERTY_TYPES.get(data["property_type"], data["property_type"]).lower())
    owner_type = html.escape(OWNER_TYPES.get(data["owner_type"], data["owner_type"]))
    travel_type = html.escape(TRAVEL_TYPES_RU.get(data["travel_type"], data["travel_type"]))
    metro = html.escape(str(data.get("metro", "")))
    floor = html.escape(str(data.get("floor", "")))
    address = html.escape(str(data.get("address", "")))
    description = html.escape(str(data.get("description", "")).strip())
    username_safe = html.escape(username)
    area_display = _format_number(data.get("area"))
    rooms_display = _format_number(data.get("rooms"))
    price_display = _format_price(data.get("price"))

    selected_amenities = set(data.get("amenities", []))
    amenities_parts = [html.escape(item) for item in AMENITIES if item in selected_amenities]
    amenities = " • ".join(amenities_parts) if amenities_parts else "Без дополнительных удобств"

    metro_tag = str(data.get("metro", "")).replace(" ", "_")
    rooms_value = int(float(data.get("rooms", 1) or 1))
    price_value = int(data.get("price", 0) or 0)
    price_tag = _price_tag(price_value)
    room_tags = {
        1: "#однушка",
        2: "#двушка",
        3: "#трешка",
        4: "#4комнаты",
        5: "#5комнат",
        6: "#6комнат",
    }
    room_tag = room_tags.get(rooms_value, "#квартира")

    return (
        f"<b>{rooms_display}-к {property_type}, {area_display} м2 | {price_display} р/мес</b>\n\n"
        f"м. {metro}\n\n"
        f"• {data['travel_time']} минут {travel_type}\n"
        f"• {floor}\n"
        f"• {address}\n\n"
        f"{owner_type}\n\n"
        f"<blockquote>{description}</blockquote>\n\n"
        f"{amenities}\n\n"
        f"Контакт: @{username_safe}\n\n"
        f"#{metro_tag} {price_tag} {room_tag} #аренда"
    )


def listing_to_text_payload(listing) -> dict:
    amenities = listing.amenities or []
    return {
        "property_type": listing.property_type.value if listing.property_type else "",
        "owner_type": listing.owner_type.value if listing.owner_type else "",
        "area": listing.area,
        "rooms": listing.rooms,
        "price": listing.price,
        "floor": listing.floor,
        "metro": listing.metro,
        "travel_type": listing.travel_type,
        "travel_time": listing.travel_time,
        "address": listing.address,
        "description": listing.description,
        "amenities": amenities,
    }
