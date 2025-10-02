from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation


def parse_decimal(value: str | float | int | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = re.sub(r"[^0-9,.-]", "", value).replace(",", ".")
    try:
        return float(Decimal(cleaned))
    except InvalidOperation:
        return None
