"""Tests for app/core/dates.py (Roadmap Tasks T1.6)."""

from datetime import date

import pytest

from app.core import dates


def test_format_date_uses_day_month_name_year():
    assert dates.format_date(date(2026, 10, 20)) == "20-Oct-2026"


def test_format_date_pads_single_digit_day():
    assert dates.format_date(date(2027, 1, 1)) == "01-Jan-2027"


def test_parse_dash_format():
    assert dates.parse_date("20-Oct-2026") == date(2026, 10, 20)


def test_parse_slash_format():
    assert dates.parse_date("20/10/2026") == date(2026, 10, 20)


def test_parse_is_case_insensitive_for_month_name():
    assert dates.parse_date("20-OCT-2026") == date(2026, 10, 20)


def test_parse_strips_spaces():
    assert dates.parse_date("  20/10/2026  ") == date(2026, 10, 20)


@pytest.mark.parametrize("text", ["31/02/2026", "29-Feb-2027", "32-Oct-2026", "20-Xyz-2026", "2026-10-20", "hello", ""])
def test_parse_rejects_invalid_text(text):
    assert dates.parse_date(text) is None


def test_leap_day_is_accepted_in_leap_year():
    assert dates.parse_date("29-Feb-2028") == date(2028, 2, 29)


def test_folder_names_match_pattern():
    assert dates.year_folder_name(date(2026, 10, 20)) == "2026"
    assert dates.month_folder_name(date(2026, 10, 20)) == "10-Oct"


def test_format_date_slash_is_day_month_year():
    assert dates.format_date_slash(date(2026, 10, 5)) == "05/10/2026"
