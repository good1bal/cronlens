"""Tests for cronlens.pauser."""

from datetime import datetime

import pytest

from cronlens.parser import CronExpression
from cronlens.pauser import QuietWindow, PauseResult, find_pauses


def _expr(s: str) -> CronExpression:
    return CronExpression(s)


REF = datetime(2024, 1, 15, 0, 0)


# ---------------------------------------------------------------------------
# QuietWindow
# ---------------------------------------------------------------------------

def test_quiet_window_duration_minutes():
    start = datetime(2024, 1, 15, 6, 0)
    end = datetime(2024, 1, 15, 8, 30)
    w = QuietWindow(start=start, end=end)
    assert w.duration_minutes == 150


def test_quiet_window_zero_gap():
    t = datetime(2024, 1, 15, 6, 0)
    w = QuietWindow(start=t, end=t)
    assert w.duration_minutes == 0


# ---------------------------------------------------------------------------
# PauseResult
# ---------------------------------------------------------------------------

def test_pause_result_longest_none_when_empty():
    r = PauseResult(expression="* * * * *", window_hours=24)
    assert r.longest is None


def test_pause_result_total_quiet_minutes_empty():
    r = PauseResult(expression="* * * * *", window_hours=24)
    assert r.total_quiet_minutes == 0


def test_pause_result_longest_picks_max():
    r = PauseResult(expression="0 * * * *", window_hours=24)
    r.windows = [
        QuietWindow(datetime(2024, 1, 15, 1, 0), datetime(2024, 1, 15, 3, 0)),
        QuietWindow(datetime(2024, 1, 15, 5, 0), datetime(2024, 1, 15, 9, 0)),
    ]
    assert r.longest.duration_minutes == 240


def test_pause_result_str_contains_expression():
    r = PauseResult(expression="0 * * * *", window_hours=24)
    assert "0 * * * *" in str(r)


def test_pause_result_str_contains_window():
    r = PauseResult(expression="0 * * * *", window_hours=12)
    assert "12" in str(r)


# ---------------------------------------------------------------------------
# find_pauses
# ---------------------------------------------------------------------------

def test_find_pauses_returns_pause_result():
    result = find_pauses(_expr("0 * * * *"), ref=REF, window_hours=24)
    assert isinstance(result, PauseResult)


def test_every_minute_no_quiet_windows():
    result = find_pauses(_expr("* * * * *"), ref=REF, window_hours=2, min_gap_minutes=60)
    assert len(result.windows) == 0


def test_hourly_has_quiet_windows():
    result = find_pauses(_expr("0 * * * *"), ref=REF, window_hours=24, min_gap_minutes=30)
    assert len(result.windows) > 0


def test_hourly_gap_is_60_minutes():
    result = find_pauses(_expr("0 * * * *"), ref=REF, window_hours=6, min_gap_minutes=30)
    for w in result.windows:
        assert w.duration_minutes == 60


def test_min_gap_filters_short_windows():
    # hourly schedule → 60-min gaps; asking for >60 should yield nothing
    result = find_pauses(_expr("0 * * * *"), ref=REF, window_hours=6, min_gap_minutes=61)
    assert len(result.windows) == 0


def test_window_hours_less_than_one_raises():
    with pytest.raises(ValueError, match="window_hours"):
        find_pauses(_expr("* * * * *"), ref=REF, window_hours=0)


def test_min_gap_less_than_one_raises():
    with pytest.raises(ValueError, match="min_gap_minutes"):
        find_pauses(_expr("* * * * *"), ref=REF, min_gap_minutes=0)


def test_expression_stored_in_result():
    result = find_pauses(_expr("0 9 * * 1-5"), ref=REF, window_hours=48)
    assert result.expression != ""


def test_window_hours_stored():
    result = find_pauses(_expr("0 * * * *"), ref=REF, window_hours=8)
    assert result.window_hours == 8
