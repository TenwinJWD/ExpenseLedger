"""Expense Report rules: filters, search, order, totals, pagination, and the summary cards (PRD FR-18 to FR-21c, FR-18a).

Everything here works on plain lists of Entry objects, so it can be tested without any screen.
"""

import calendar
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal

from app.core import dates, money
from app.core.models import Entry

DATE_RANGES = ("all", "this-month", "last-month", "this-year", "custom")


@dataclass
class Filters:
    """What the user chose in the filter card. 'ALL' means no limit."""

    date_range: str = "all"
    from_text: str = ""
    to_text: str = ""
    main_head: str = "ALL"
    sub_head: str = "ALL"
    name_text: str = ""
    particulars_text: str = ""
    debit_min: str = ""
    debit_max: str = ""
    credit_min: str = ""
    credit_max: str = ""
    search_text: str = ""


@dataclass
class ResolvedFilters:
    """Filters after checking. Dates and amounts are real values, or None when not used."""

    start: date | None = None
    end: date | None = None
    main_head: str = "ALL"
    sub_head: str = "ALL"
    name_text: str = ""
    particulars_text: str = ""
    debit_min: Decimal | None = None
    debit_max: Decimal | None = None
    credit_min: Decimal | None = None
    credit_max: Decimal | None = None
    search_text: str = ""


@dataclass
class Ranked:
    """A sub-head with its totals, used for the summary cards."""

    name: str
    debit: Decimal
    credit: Decimal


@dataclass
class Summary:
    """The six summary values for one month or one year (PRD FR-21a, FR-21b)."""

    debit_total: Decimal = Decimal("0.00")
    credit_total: Decimal = Decimal("0.00")
    most_debit: Ranked | None = None
    least_debit: Ranked | None = None
    most_credit: Ranked | None = None
    least_credit: Ranked | None = None


def resolve_filters(filters: Filters, today: date) -> tuple[ResolvedFilters | None, str]:
    """Check the filter values. Returns (filters, '') or (None, message) if a value is wrong."""
    start, end, error = _date_bounds(filters, today)
    if error:
        return None, error
    debit_min, debit_max = _amount_pair(filters.debit_min, filters.debit_max)
    credit_min, credit_max = _amount_pair(filters.credit_min, filters.credit_max)
    for value in (filters.debit_min, filters.debit_max, filters.credit_min, filters.credit_max):
        if value.strip() and money.parse_amount(value) is None:
            return None, "Amount filters: enter numbers like 2,500.00 with up to 2 decimals."
    if _from_above_to(debit_min, debit_max) or _from_above_to(credit_min, credit_max):
        return None, 'The "From" amount must not be more than the "To" amount.'
    return ResolvedFilters(
        start=start,
        end=end,
        main_head=filters.main_head,
        sub_head=filters.sub_head,
        name_text=filters.name_text.strip(),
        particulars_text=filters.particulars_text.strip(),
        debit_min=debit_min,
        debit_max=debit_max,
        credit_min=credit_min,
        credit_max=credit_max,
        search_text=filters.search_text.strip(),
    ), ""


def date_bounds_for_range(range_name: str, today: date) -> tuple[date | None, date | None]:
    """Start and end of a preset range (This Month, Last Month, This Year). 'all' gives no limit."""
    if range_name == "this-month":
        return _month_start(today.year, today.month), _month_end(today.year, today.month)
    if range_name == "last-month":
        year, month = (today.year - 1, 12) if today.month == 1 else (today.year, today.month - 1)
        return _month_start(year, month), _month_end(year, month)
    if range_name == "this-year":
        return date(today.year, 1, 1), date(today.year, 12, 31)
    return None, None


def filter_entries(entries: list[Entry], filters: ResolvedFilters) -> list[Entry]:
    """Entries that match every filter. Search matches name, particulars, or an amount (FR-19a)."""
    search = filters.search_text.lower()
    digits = filters.search_text.replace(",", "")
    numeric_search = digits.replace(".", "", 1).isdigit()
    result = []
    for entry in entries:
        if filters.main_head != "ALL" and entry.main_head != filters.main_head:
            continue
        if filters.sub_head != "ALL" and entry.sub_head != filters.sub_head:
            continue
        if filters.start and entry.entry_date < filters.start:
            continue
        if filters.end and entry.entry_date > filters.end:
            continue
        if filters.name_text and filters.name_text.lower() not in entry.name.lower():
            continue
        if filters.particulars_text and filters.particulars_text.lower() not in entry.particulars.lower():
            continue
        if not _in_range(entry.debit, filters.debit_min, filters.debit_max):
            continue
        if not _in_range(entry.credit, filters.credit_min, filters.credit_max):
            continue
        if search:
            text_hit = search in entry.name.lower() or search in entry.particulars.lower()
            amount_hit = numeric_search and any(
                f"{value:.2f}".find(digits) >= 0 for value in (entry.debit, entry.credit)
            )
            if not (text_hit or amount_hit):
                continue
        result.append(entry)
    return result


def sort_oldest_first(entries: list[Entry]) -> list[Entry]:
    return sorted(entries, key=lambda entry: (entry.entry_date, entry.id))


def sort_newest_first(entries: list[Entry]) -> list[Entry]:
    return sorted(entries, key=lambda entry: (entry.entry_date, entry.id), reverse=True)


def totals(entries: list[Entry]) -> tuple[Decimal, Decimal]:
    """Total debit and total credit of the given rows (PRD FR-20)."""
    return (
        sum((entry.debit for entry in entries), Decimal("0.00")),
        sum((entry.credit for entry in entries), Decimal("0.00")),
    )


def summarize(entries: list[Entry]) -> Summary:
    """The six summary values. Only sub-heads with at least one entry are ranked (FR-21c)."""
    groups: dict[str, Ranked] = {}
    for entry in entries:
        group = groups.setdefault(entry.sub_head, Ranked(entry.sub_head, Decimal("0.00"), Decimal("0.00")))
        group.debit += entry.debit
        group.credit += entry.credit
    ranked = list(groups.values())
    summary = Summary()
    summary.debit_total, summary.credit_total = totals(entries)
    if ranked:
        by_debit = sorted(ranked, key=lambda item: (item.debit, item.name))
        by_credit = sorted(ranked, key=lambda item: (item.credit, item.name))
        summary.least_debit, summary.most_debit = by_debit[0], by_debit[-1]
        summary.least_credit, summary.most_credit = by_credit[0], by_credit[-1]
    return summary


@dataclass
class Bar:
    """One bar group of a Dashboard chart: a month of the year, or a day of the month."""

    label: str
    debit: Decimal
    credit: Decimal


def monthly_series(entries: list[Entry], year: int) -> list[Bar]:
    """Debit and credit for each month of the year, January to December (Dashboard yearly chart)."""
    bars = [Bar(calendar.month_abbr[month], Decimal("0.00"), Decimal("0.00")) for month in range(1, 13)]
    for entry in entries:
        if entry.entry_date.year == year:
            bar = bars[entry.entry_date.month - 1]
            bar.debit += entry.debit
            bar.credit += entry.credit
    return bars


def daily_series(entries: list[Entry], year: int, month: int) -> list[Bar]:
    """Debit and credit for each day of the month (Dashboard monthly chart)."""
    days = calendar.monthrange(year, month)[1]
    bars = [Bar(str(day), Decimal("0.00"), Decimal("0.00")) for day in range(1, days + 1)]
    for entry in entries:
        if entry.entry_date.year == year and entry.entry_date.month == month:
            bar = bars[entry.entry_date.day - 1]
            bar.debit += entry.debit
            bar.credit += entry.credit
    return bars


def month_key(entry: Entry) -> str:
    return f"{entry.entry_date.year}-{entry.entry_date.month:02d}"


def entries_in_month(entries: list[Entry], year: int, month: int) -> list[Entry]:
    return [entry for entry in entries if entry.entry_date.year == year and entry.entry_date.month == month]


def entries_in_year(entries: list[Entry], year: int) -> list[Entry]:
    return [entry for entry in entries if entry.entry_date.year == year]


def page_slice(rows: list, page: int, page_size: int) -> tuple[list, int]:
    """The rows for one page, and the corrected page number (FR-18a)."""
    pages = max(1, -(-len(rows) // page_size))
    page = min(max(1, page), pages)
    start = (page - 1) * page_size
    return rows[start:start + page_size], page


# ----- helpers -----

def _month_start(year: int, month: int) -> date:
    return date(year, month, 1)


def _month_end(year: int, month: int) -> date:
    if month == 12:
        return date(year, 12, 31)
    return date(year, month + 1, 1) - timedelta(days=1)


def _date_bounds(filters: Filters, today: date) -> tuple[date | None, date | None, str]:
    if filters.date_range != "custom":
        start, end = date_bounds_for_range(filters.date_range, today)
        return start, end, ""
    start = end = None
    if filters.from_text.strip():
        start = dates.parse_date(filters.from_text)
        if start is None:
            return None, None, "From date: enter as 20-Oct-2026 or 20/10/2026."
    if filters.to_text.strip():
        end = dates.parse_date(filters.to_text)
        if end is None:
            return None, None, "To date: enter as 20-Oct-2026 or 20/10/2026."
    if start and end and start > end:
        return None, None, "From date must be before To date."
    return start, end, ""


def _amount_pair(low: str, high: str) -> tuple[Decimal | None, Decimal | None]:
    return (money.parse_amount(low) if low.strip() else None,
            money.parse_amount(high) if high.strip() else None)


def _from_above_to(low: Decimal | None, high: Decimal | None) -> bool:
    return low is not None and high is not None and low > high


def _in_range(value: Decimal, low: Decimal | None, high: Decimal | None) -> bool:
    if low is not None and value < low:
        return False
    if high is not None and value > high:
        return False
    return True
