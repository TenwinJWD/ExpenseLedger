"""Tests for app/services/report_service.py (Roadmap Tasks T7.3 and T7.5)."""

from datetime import date, datetime
from decimal import Decimal

import pytest

from app.core.models import Entry
from app.services import report_service as rs

TODAY = date(2026, 10, 24)


def entry(entry_id, entry_date, sub_head, name, particulars, debit, credit, main_head="MH 2"):
    return Entry(
        id=entry_id,
        main_head=main_head,
        sub_head=sub_head,
        entry_date=entry_date,
        name=name,
        particulars=particulars,
        debit=Decimal(debit),
        credit=Decimal(credit),
        created_at=datetime(2026, 10, 1, 9, 0),
    )


@pytest.fixture
def rows():
    return [
        entry("E20261001-001", date(2026, 10, 1), "Lenin", "Lenin", "Morning milk", "1000.00", "0.00"),
        entry("E20261020-001", date(2026, 10, 20), "Office Expense", "Vendor Account", "Operational Expense", "2500.00", "14200.00", "MH 1"),
        entry("E20260915-001", date(2026, 9, 15), "Lenin", "Lenin", "Old entry", "300.00", "50.00"),
        entry("E20250301-001", date(2025, 3, 1), "Rent", "Landlord", "Last year", "900.00", "0.00", "MH 1"),
    ]


def resolve(**changes):
    filters, error = rs.resolve_filters(rs.Filters(**changes), TODAY)
    assert error == ""
    return filters


# ----- filters (T7.1) -----

def test_no_filter_keeps_every_row(rows):
    assert len(rs.filter_entries(rows, resolve())) == 4


def test_main_head_filter(rows):
    result = rs.filter_entries(rows, resolve(main_head="MH 1"))
    assert {e.id for e in result} == {"E20261020-001", "E20250301-001"}


def test_sub_head_filter(rows):
    assert [e.id for e in rs.filter_entries(rows, resolve(sub_head="Lenin"))] == ["E20261001-001", "E20260915-001"]


def test_this_month_range(rows):
    result = rs.filter_entries(rows, resolve(date_range="this-month"))
    assert {e.id for e in result} == {"E20261001-001", "E20261020-001"}


def test_last_month_range(rows):
    result = rs.filter_entries(rows, resolve(date_range="last-month"))
    assert [e.id for e in result] == ["E20260915-001"]


def test_this_year_range(rows):
    result = rs.filter_entries(rows, resolve(date_range="this-year"))
    assert len(result) == 3


def test_custom_range_is_inclusive(rows):
    result = rs.filter_entries(rows, resolve(date_range="custom", from_text="01-Oct-2026", to_text="20/10/2026"))
    assert {e.id for e in result} == {"E20261001-001", "E20261020-001"}


def test_custom_range_bad_date_is_refused():
    filters, error = rs.resolve_filters(rs.Filters(date_range="custom", from_text="31/02/2026"), TODAY)
    assert filters is None
    assert error == "From date: enter as 20-Oct-2026 or 20/10/2026."


def test_custom_range_from_after_to_is_refused():
    filters, error = rs.resolve_filters(rs.Filters(date_range="custom", from_text="20-Oct-2026", to_text="01-Oct-2026"), TODAY)
    assert filters is None
    assert error == "From date must be before To date."


def test_name_and_particulars_contain_match(rows):
    assert [e.id for e in rs.filter_entries(rows, resolve(name_text="vendor"))] == ["E20261020-001"]
    assert [e.id for e in rs.filter_entries(rows, resolve(particulars_text="old"))] == ["E20260915-001"]


def test_debit_range_is_inclusive(rows):
    result = rs.filter_entries(rows, resolve(debit_min="1,000.00", debit_max="2500"))
    assert {e.id for e in result} == {"E20261001-001", "E20261020-001"}


def test_credit_min_only(rows):
    assert {e.id for e in rs.filter_entries(rows, resolve(credit_min="100"))} == {"E20261020-001"}


def test_amount_filter_from_above_to_is_refused():
    filters, error = rs.resolve_filters(rs.Filters(debit_min="500", debit_max="100"), TODAY)
    assert filters is None
    assert error == 'The "From" amount must not be more than the "To" amount.'


def test_bad_amount_filter_is_refused():
    filters, error = rs.resolve_filters(rs.Filters(credit_max="abc"), TODAY)
    assert filters is None


def test_filters_combine(rows):
    result = rs.filter_entries(rows, resolve(main_head="MH 2", date_range="this-month", debit_min="500"))
    assert [e.id for e in result] == ["E20261001-001"]


# ----- search (T7.2) -----

@pytest.mark.parametrize("text, expected", [
    ("vendor", ["E20261020-001"]),
    ("morning", ["E20261001-001"]),
    ("2500", ["E20261020-001"]),
    ("2500.00", ["E20261020-001"]),
    ("2,500", ["E20261020-001"]),
    ("14200", ["E20261020-001"]),
    ("zzz", []),
])
def test_search_by_name_particulars_or_amount(rows, text, expected):
    assert [e.id for e in rs.filter_entries(rows, resolve(search_text=text))] == expected


def test_search_is_combined_with_other_filters(rows):
    assert rs.filter_entries(rows, resolve(search_text="2500", main_head="MH 2")) == []


# ----- order and totals (T7.3) -----

def test_sort_is_oldest_first(rows):
    assert [e.entry_date for e in rs.sort_oldest_first(rows)] == sorted(e.entry_date for e in rows)


def test_totals_of_shown_rows(rows):
    debit, credit = rs.totals(rows[:2])
    assert debit == Decimal("3500.00")
    assert credit == Decimal("14200.00")


def test_totals_of_no_rows_are_zero():
    assert rs.totals([]) == (Decimal("0.00"), Decimal("0.00"))


# ----- summary cards (T7.4 and T7.5) -----

def test_summary_totals_and_extremes(rows):
    october = rs.entries_in_month(rows, 2026, 10)
    summary = rs.summarize(october)
    assert summary.debit_total == Decimal("3500.00")
    assert summary.credit_total == Decimal("14200.00")
    assert summary.most_debit.name == "Office Expense"
    assert summary.least_debit.name == "Lenin"
    assert summary.most_credit.name == "Office Expense"
    assert summary.least_credit.name == "Lenin"


def test_summary_ranks_only_sub_heads_with_entries(rows):
    year = rs.entries_in_year(rows, 2026)
    summary = rs.summarize(year)
    names = {summary.most_debit.name, summary.least_debit.name}
    assert "Rent" not in names


def test_summary_ties_are_broken_by_name():
    tied = [
        entry("A", date(2026, 10, 1), "Beta", "x", "x", "100", "0"),
        entry("B", date(2026, 10, 2), "Alpha", "x", "x", "100", "0"),
    ]
    summary = rs.summarize(tied)
    assert summary.least_debit.name == "Alpha"
    assert summary.most_debit.name == "Beta"


def test_empty_period_has_zero_totals_and_no_ranking():
    summary = rs.summarize([])
    assert summary.debit_total == Decimal("0.00")
    assert summary.most_debit is None and summary.least_debit is None


def test_yearly_and_monthly_are_separate(rows):
    assert len(rs.entries_in_month(rows, 2026, 10)) == 2
    assert len(rs.entries_in_year(rows, 2026)) == 3


def test_month_range_end_for_december():
    assert rs.date_bounds_for_range("this-year", date(2026, 12, 5)) == (date(2026, 1, 1), date(2026, 12, 31))
    assert rs._month_end(2026, 12) == date(2026, 12, 31)
    assert rs._month_end(2026, 2) == date(2026, 2, 28)


def test_last_month_wraps_into_previous_year():
    assert rs.date_bounds_for_range("last-month", date(2026, 1, 10)) == (date(2025, 12, 1), date(2025, 12, 31))


# ----- pagination (FR-18a) -----

def test_page_slice_and_clamping():
    rows = list(range(25))
    assert rs.page_slice(rows, 1, 10)[0] == list(range(10))
    assert rs.page_slice(rows, 3, 10) == (list(range(20, 25)), 3)
    assert rs.page_slice(rows, 9, 10) == (list(range(20, 25)), 3)
    assert rs.page_slice([], 1, 10) == ([], 1)
