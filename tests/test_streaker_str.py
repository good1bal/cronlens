"""Tests for StreakResult.__str__ formatting."""

from __future__ import annotations

from datetime import datetime

from cronlens.parser import CronExpression
from cronlens.streaker import StreakResult, find_streaks

REF = datetime(2024, 3, 20, 8, 0)


def _result() -> StreakResult:
    return find_streaks(CronExpression("* * * * *"), window_days=3, ref=REF)


def test_str_contains_expression_label():
    assert "Expression" in str(_result())


def test_str_contains_window_label():
    assert "Window" in str(_result())


def test_str_contains_active_days_label():
    assert "Active days" in str(_result())


def test_str_contains_active_hours_label():
    assert "Active hrs" in str(_result())


def test_str_contains_longest_day_streak_label():
    assert "Longest day streak" in str(_result())


def test_str_contains_longest_hour_streak_label():
    assert "Longest hour streak" in str(_result())


def test_str_is_multiline():
    lines = str(_result()).splitlines()
    assert len(lines) >= 6
