"""Tests for app/core/validation.py (Roadmap Tasks T5.2)."""

from datetime import date
from decimal import Decimal

import pytest

from app.core import config
from app.core.validation import check_entry

GOOD = dict(
    sub_head_chosen=True,
    date_text="20-Oct-2026",
    name="Lenin",
    particulars="Morning collection",
    debit_text="0.00",
    credit_text="250.50",
)


def with_changes(**changes):
    values = dict(GOOD)
    values.update(changes)
    return check_entry(**values)


def test_good_entry_is_valid_and_returns_values():
    result = with_changes()
    assert result.valid
    assert result.errors == {}
    assert result.values["date"] == date(2026, 10, 20)
    assert result.values["credit"] == Decimal("250.50")


def test_no_sub_head_disables_submit():
    result = with_changes(sub_head_chosen=False)
    assert not result.valid
    assert result.errors == {}


def test_debit_and_credit_both_zero_is_invalid():
    result = with_changes(debit_text="0.00", credit_text="0")
    assert not result.valid
    assert result.both_zero


def test_one_amount_above_zero_is_enough():
    assert with_changes(debit_text="5", credit_text="0.00").valid


def test_both_amounts_may_be_above_zero():
    assert with_changes(debit_text="5", credit_text="6").valid


@pytest.mark.parametrize("text", ["-5", "2.555", "abc"])
def test_bad_amounts_are_reported(text):
    result = with_changes(debit_text=text)
    assert "debit" in result.errors
    assert not result.valid


@pytest.mark.parametrize("text", ["31/02/2026", "not a date", ""])
def test_bad_dates_are_reported(text):
    result = with_changes(date_text=text)
    assert "date" in result.errors


def test_slash_date_is_accepted():
    result = with_changes(date_text="20/10/2026")
    assert result.valid
    assert result.values["date"] == date(2026, 10, 20)


def test_empty_name_and_particulars_are_reported():
    result = with_changes(name="   ", particulars="")
    assert result.errors["name"] == "Name is required."
    assert result.errors["particulars"] == "Particulars is required."


def test_name_at_limit_is_valid_and_one_over_is_not():
    assert with_changes(name="n" * config.NAME_MAX_LENGTH).valid
    too_long = with_changes(name="n" * (config.NAME_MAX_LENGTH + 1))
    assert "name" in too_long.errors


def test_particulars_at_limit_is_valid_and_one_over_is_not():
    assert with_changes(particulars="p" * config.PARTICULARS_MAX_LENGTH).valid
    too_long = with_changes(particulars="p" * (config.PARTICULARS_MAX_LENGTH + 1))
    assert "particulars" in too_long.errors


def test_blank_amounts_count_as_zero_placeholder():
    result = with_changes(debit_text="", credit_text="250")
    assert result.valid
    assert result.values["debit"] == Decimal("0.00")


def test_both_blank_amounts_are_invalid():
    result = with_changes(debit_text="", credit_text="")
    assert not result.valid
    assert result.both_zero
