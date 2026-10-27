"""Tests for app/core/money.py (Roadmap Tasks T1.8)."""

from decimal import Decimal

import pytest

from app.core import money


@pytest.mark.parametrize(
    "text, expected",
    [
        ("2500", Decimal("2500.00")),
        ("2500.5", Decimal("2500.50")),
        ("2,500.00", Decimal("2500.00")),
        ("122,500", Decimal("122500.00")),
        ("0", Decimal("0.00")),
        ("  14200.25  ", Decimal("14200.25")),
    ],
)
def test_parse_valid_amounts(text, expected):
    assert money.parse_amount(text) == expected


@pytest.mark.parametrize("text", ["2500.001", "-5", "abc", "", "1.2.3", "1,2,3.5x"])
def test_parse_rejects_invalid_amounts(text):
    assert money.parse_amount(text) is None


@pytest.mark.parametrize(
    "value, expected",
    [
        (Decimal("0"), "0.00"),
        (Decimal("2500"), "2,500.00"),
        (Decimal("14200.5"), "14,200.50"),
        (Decimal("122500"), "122,500.00"),
    ],
)
def test_format_amount(value, expected):
    assert money.format_amount(value) == expected
