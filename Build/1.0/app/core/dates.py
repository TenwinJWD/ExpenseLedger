"""Date helpers. The only place that formats or parses dates (PRD FR-28, FR-32, FR-33).

Dates show as DD-Mon-YYYY (for example 20-Oct-2026). Typed dates may also be
DD/MM/YYYY. Month names come from a fixed list so the output does not depend on
the Windows language setting (Rules 12).
"""

import re
from datetime import date

MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

_DASH_PATTERN = re.compile(r"^(\d{1,2})-([A-Za-z]{3})-(\d{4})$")
_SLASH_PATTERN = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")


def format_date(value: date) -> str:
    """Return the date as DD-Mon-YYYY, for example 20-Oct-2026."""
    return f"{value.day:02d}-{MONTHS[value.month - 1]}-{value.year}"


def format_date_slash(value: date) -> str:
    """Return the date as DD/MM/YYYY, for example 20/10/2026. Used on screen only, since / is not allowed in file names."""
    return f"{value.day:02d}/{value.month:02d}/{value.year}"


def parse_date(text: str) -> date | None:
    """Parse DD-Mon-YYYY or DD/MM/YYYY. Return None if the text is not a real date."""
    text = text.strip()
    match = _SLASH_PATTERN.match(text)
    if match:
        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
    else:
        match = _DASH_PATTERN.match(text)
        if not match:
            return None
        day = int(match.group(1))
        month_name = match.group(2).capitalize()
        if month_name not in MONTHS:
            return None
        month = MONTHS.index(month_name) + 1
        year = int(match.group(3))
    try:
        return date(year, month, day)  # rejects 31-Feb and similar
    except ValueError:
        return None


def year_folder_name(value: date) -> str:
    """The year folder in the data folder, for example 2026."""
    return str(value.year)


def month_folder_name(value: date) -> str:
    """The month folder in the data folder, for example 10-Oct."""
    return f"{value.month:02d}-{MONTHS[value.month - 1]}"
