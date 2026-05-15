"""Tests for cronlens.streaker."""

from __future__ import annotations

from datetime import datetime

import pytest

from cronlens.parser import CronExpression
from cronlens.streaker import StreakResult, find_streaks


def _expr(s: str) -> CronExpression:
    return CronExpression(s)


REF = datetime(2024, 6, 15, 12, 0)


def test_find_streaks_returns_streak_result():
    result = find_streaks(_expr("* * * * *"), window_days=1, ref=REF)
    assert isinstance(result, StreakResult)


def test_every_minute_active_days_equals_window():
    result = find_streaks(_expr("* * * * *"), window_days=3, ref=REF)
    assert result.active_days == 3


def test_every_minute_longest_day_streak_equals_window():
    result = find_streaks(_expr("* * * * *"), window_days=5, ref=REF)
    assert result.longest_day_streak == 5


def test_every_minute_active_hours_equals_window_hours():
    result = find_streaks(_expr("* * * * *"), window_days=2, ref=REF)
    # 2 days = 48 hours, but ref is noon so window ends at noon two days prior
    assert result.active_hours == 48


def test_every_minute_longest_hour_streak_equals_active_hours():
    result = find_streaks(_expr("* * * * *"), window_days=2, ref=REF)
    assert result.longest_hour_streak == result.active_hours


def test_hourly_expression_active_hours_correct():
    # "0 * * * *" fires once per hour
    result = find_streaks(_expr("0 * * * *"), window_days=1, ref=REF)
    assert result.active_hours == 24


def test_daily_expression_active_days():
    # fires once per day at midnight
    result = find_streaks(_expr("0 0 * * *"), window_days=7, ref=REF)
    assert result.active_days == 7


def test_window_days_stored():
    result = find_streaks(_expr("* * * * *"), window_days=10, ref=REF)
    assert result.window_days == 10


def test_expression_stored():
    expr = _expr("*/5 * * * *")
    result = find_streaks(expr, window_days=1, ref=REF)
    assert result.expression == repr(expr)


def test_invalid_window_raises():
    with pytest.raises(ValueError):
        find_streaks(_expr("* * * * *"), window_days=0, ref=REF)


def test_day_streaks_list_is_list():
    result = find_streaks(_expr("* * * * *"), window_days=3, ref=REF)
    assert isinstance(result.day_streaks, list)


def test_hour_streaks_list_is_list():
    result = find_streaks(_expr("* * * * *"), window_days=2, ref=REF)
    assert isinstance(result.hour_streaks, list)


def test_str_contains_expression():
    expr = _expr("*/10 * * * *")
    result = find_streaks(expr, window_days=1, ref=REF)
    assert repr(expr) in str(result)


def test_str_contains_window():
    result = find_streaks(_expr("* * * * *"), window_days=14, ref=REF)
    assert "14" in str(result)
