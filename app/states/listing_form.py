from aiogram.fsm.state import State, StatesGroup


class ListingForm(StatesGroup):
    property_type = State()
    owner_type = State()
    area = State()
    rooms = State()
    price = State()
    floor = State()
    metro = State()
    travel_type = State()
    travel_time = State()
    address = State()
    amenities = State()
    description = State()
    photos = State()
    edit_value = State()
    edit_photos = State()
