"""Tests for cronlens.calendar_view."""

from __future__ import annotations

import pytest
from unittest.mock import patch
from datetime import datetime

from cronlens.parser import CronExpression
from cronlens.calendar_view import build_calendar, CalendarResult, DAY_NAMES


def _expr(s: str) -> CronExpression:
    return CronExpression(s)


def test_build_calendar_returns_calendar_result():
    result = build_calendar(_expr("* * * * *"), weeks=1)
    assert isinstance(result, CalendarResult)


def test_grid_shape():
    result = build_calendar(_expr("* * * * *"), weeks=1)
    assert len(result.grid) == 7
    assert all(len(row) == 24 for row in result.grid)


def test_every_minute_has_nonzero_total():
    result = build_calendar(_expr("* * * * *"), weeks=1)
    assert result.total > 0


def test_expression_stored():
    expr = _expr("0 9 * * 1")
    result = build_calendar(expr, weeks=1)
    assert result.expression == str(expr)


def test_weeks_stored():
    result = build_calendar(_expr("* * * * *"), weeks=2)
    assert result.weeks == 2


def test_specific_hour_only_fires_in_that_hour():
    result = build_calendar(_expr("0 9 * * *"), weeks=1)
    for dow in range(7):
        for hour in range(24):
            if hour != 9:
                assert result.grid[dow][hour] == 0, f"Unexpected fire at dow={dow} hour={hour}"


def test_peak_equals_max_cell():
    result = build_calendar(_expr("0 * * * *"), weeks=1)
    expected = max(cell for row in result.grid for cell in row)
    assert result.peak == expected


def test_total_equals_sum_of_cells():
    result = build_calendar(_expr("0 * * * *"), weeks=1)
    expected = sum(cell for row in result.grid for cell in row)
    assert result.total == expected


def test_weeks_less_than_one_raises():
    with pytest.raises(ValueError):
        build_calendar(_expr("* * * * *"), weeks=0)


def test_str_contains_expression():
    expr = _expr("*/15 * * * *")
    result = build_calendar(expr, weeks=1)
    assert str(expr) in str(result)


def test_str_contains_day_names():
    result = build_calendar(_expr("* * * * *"), weeks=1)
    text = str(result)
    for name in DAY_NAMES:
        assert name in text


def test_str_contains_total():
    result = build_calendar(_expr("0 12 * * *"), weeks=1)
    assert "Total fires" in str(result)
