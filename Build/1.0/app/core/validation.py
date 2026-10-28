"""Rules for the Main Entry form (PRD FR-12, FR-13, FR-14; Design.md 5.3).

One place for the rules (Rules 9). The screen shows the messages returned here and
does not repeat the checks.
"""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from app.core import config, dates, money


@dataclass
class EntryCheck:
    """Result of checking the form. values is set only when every field is valid."""

    errors: dict[str, str] = field(default_factory=dict)
    values: dict | None = None
    both_zero: bool = False
    valid: bool = False


AMOUNT_MESSAGE = "Enter 0.00 or more, with up to 2 decimals."
DATE_MESSAGE = "Enter a date as 20-Oct-2026 or 20/10/2026."


def check_entry(
    sub_head_chosen: bool,
    date_text: str,
    name: str,
    particulars: str,
    debit_text: str,
    credit_text: str,
) -> EntryCheck:
    """Check every field. Submit is enabled only when valid is True (FR-14)."""
    errors: dict[str, str] = {}

    entry_date: date | None = dates.parse_date(date_text)
    if entry_date is None:
        errors["date"] = DATE_MESSAGE

    name = name.strip()
    if not name:
        errors["name"] = "Name is required."
    elif len(name) > config.NAME_MAX_LENGTH:
        errors["name"] = f"Name can be up to {config.NAME_MAX_LENGTH} characters."

    particulars = particulars.strip()
    if not particulars:
        errors["particulars"] = "Particulars is required."
    elif len(particulars) > config.PARTICULARS_MAX_LENGTH:
        errors["particulars"] = f"Particulars can be up to {config.PARTICULARS_MAX_LENGTH} characters."

    # A blank amount shows the 0.00 placeholder and counts as zero.
    debit: Decimal | None = money.parse_amount(debit_text.strip() or "0")
    if debit is None:
        errors["debit"] = AMOUNT_MESSAGE
    credit: Decimal | None = money.parse_amount(credit_text.strip() or "0")
    if credit is None:
        errors["credit"] = AMOUNT_MESSAGE

    both_zero = debit is not None and credit is not None and debit == 0 and credit == 0
    valid = sub_head_chosen and not errors and not both_zero
    values = None
    if not errors:
        values = {
            "date": entry_date,
            "name": name,
            "particulars": particulars,
            "debit": debit,
            "credit": credit,
        }
    return EntryCheck(errors=errors, values=values, both_zero=both_zero, valid=valid)


FORBIDDEN_NAME_CHARACTERS = ('"', "\\")


def name_error(name: str, max_length: int) -> str:
    """The message for an invalid Main Entry or Sub-Head name (already trimmed), or an empty string if it is fine."""
    if not name:
        return "Enter a name."
    if len(name) > max_length:
        return f"Use up to {max_length} characters."
    if any(character in name for character in FORBIDDEN_NAME_CHARACTERS):
        return "Quotation marks and backslashes cannot be used."
    return ""
