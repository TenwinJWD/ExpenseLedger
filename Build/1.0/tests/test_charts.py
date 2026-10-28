"""Tests for the value axis of the Dashboard chart (app/ui/charts.py). The drawing itself is checked by eye."""

from decimal import Decimal

import pytest

from app.ui.charts import TICK_COUNT, nice_axis


@pytest.mark.parametrize("highest", [0, 3, 7, 40, 999, 8200, 15000, 123456, 9999999])
def test_axis_covers_the_highest_value_with_whole_steps(highest):
    step, top = nice_axis(Decimal(highest))
    assert top == step * TICK_COUNT
    assert top >= highest
    assert step >= 1


def test_axis_does_not_waste_space():
    assert nice_axis(Decimal(8200)) == (2500, 10000)
    assert nice_axis(Decimal(15000)) == (5000, 20000)
