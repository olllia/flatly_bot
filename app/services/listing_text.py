from aiogram.types import MessageEntity

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


def format_listing_text(data: dict, username: str) -> str:
    publication_text = data.get("publication_text")
    if publication_text:
        return publication_text

    property_type = PROPERTY_TYPES.get(data["property_type"], data["property_type"]).lower()
    owner_type = OWNER_TYPES.get(data["owner_type"], data["owner_type"])
    travel_type = TRAVEL_TYPES_RU.get(data["travel_type"], data["travel_type"])
    selected_amenities = set(data.get("amenities", []))
    amenities_parts = []
    for item in AMENITIES:
        if item in selected_amenities:
            amenities_parts.append(item)
        else:
            amenities_parts.append(f"<s>{item}</s>")
    amenities = " • ".join(amenities_parts)

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
    rooms_display = str(rooms_value)

    return (
        f"{rooms_display}-к {property_type}, {data['area']} м2 | {data['price']} р/мес\n\n"
        f"м. {data['metro']}\n\n"
        f"* {data['travel_time']} минут {travel_type}\n"
        f"* {data['floor']}\n"
        f"* {data['address']}\n\n"
        f"{owner_type}\n\n"
        f"{data['description']}\n\n"
        f"{amenities}\n\n"
        f"Контакт: @{username}\n\n"
        f"#{metro_tag} {price_tag} {room_tag} #аренда"
    )


def serialize_entities(entities: list[MessageEntity] | None) -> list[dict]:
    if not entities:
        return []
    return [entity.model_dump(exclude_none=True) for entity in entities]


def deserialize_entities(entities: list[dict] | None) -> list[MessageEntity] | None:
    if not entities:
        return None
    return [MessageEntity.model_validate(entity) for entity in entities]


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
        "publication_text": listing.publication_text,
        "publication_entities": listing.publication_entities or [],
        "publication_source_chat_id": listing.publication_source_chat_id,
        "publication_source_message_id": listing.publication_source_message_id,
        "amenities": amenities,
    }
