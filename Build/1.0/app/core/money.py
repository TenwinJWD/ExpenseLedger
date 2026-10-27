"""Amount helpers. Money is always decimal.Decimal, never float (Rules 13).

Amounts show as 2,500.00. Typed amounts may include commas. Negative amounts and
more than two decimals are rejected (PRD FR-13).
"""

import re
from decimal import Decimal

_AMOUNT_PATTERN = re.compile(r"^\d+(\.\d{1,2})?$")
_CENT = Decimal("0.01")


def parse_amount(text: str) -> Decimal | None:
    """Return the amount with two decimals, or None if the text is not a valid amount."""
    cleaned = text.strip().replace(",", "")
    if not _AMOUNT_PATTERN.match(cleaned):
        return None
    return Decimal(cleaned).quantize(_CENT)


def format_amount(value: Decimal) -> str:
    """Return the amount with thousands separators and two decimals, for example 2,500.00."""
    return f"{value.quantize(_CENT):,.2f}"
