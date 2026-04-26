from decimal import Decimal, InvalidOperation


def to_positive_number(text: str) -> float | None:
    normalized = (
        text.replace("\u00a0", "")
        .replace("\u202f", "")
        .replace(" ", "")
        .replace(",", ".")
        .strip()
    )
    try:
        value = Decimal(normalized)
    except (InvalidOperation, AttributeError):
        return None
    if value <= 0:
        return None
    return float(value)


def to_positive_int(text: str) -> int | None:
    value = to_positive_number(text)
    if value is None or int(value) != value:
        return None
    return int(value)
