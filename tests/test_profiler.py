"""Tests for cronlens.profiler."""

from datetime import datetime

import pytest

from cronlens.parser import CronExpression
from cronlens.profiler import ProfileResult, profile


REF = datetime(2024, 1, 15, 0, 0, 0)


def _expr(s: str) -> CronExpression:
    return CronExpression(s)


# ---------------------------------------------------------------------------
# profile() return type
# ---------------------------------------------------------------------------

def test_profile_returns_profile_result():
    result = profile(_expr("* * * * *"), ref=REF, window_hours=1)
    assert isinstance(result, ProfileResult)


def test_profile_stores_expression():
    result = profile(_expr("* * * * *"), ref=REF, window_hours=1)
    assert "* * * * *" in result.expression


def test_profile_stores_window_hours():
    result = profile(_expr("* * * * *"), ref=REF, window_hours=6)
    assert result.window_hours == 6


# ---------------------------------------------------------------------------
# total_runs counts
# ---------------------------------------------------------------------------

def test_every_minute_total_runs_one_hour():
    result = profile(_expr("* * * * *"), ref=REF, window_hours=1)
    assert result.total_runs == 60


def test_hourly_total_runs_24h():
    result = profile(_expr("0 * * * *"), ref=REF, window_hours=24)
    assert result.total_runs == 24


def test_daily_total_runs_24h():
    result = profile(_expr("0 9 * * *"), ref=REF, window_hours=24)
    assert result.total_runs == 1


def test_total_runs_zero_when_no_match_in_window():
    # fires at 09:00 but window is only 1 hour starting at 00:00
    result = profile(_expr("0 9 * * *"), ref=REF, window_hours=1)
    assert result.total_runs == 0


# ---------------------------------------------------------------------------
# runs_per_hour
# ---------------------------------------------------------------------------

def test_runs_per_hour_has_24_keys():
    result = profile(_expr("* * * * *"), ref=REF, window_hours=24)
    assert set(result.runs_per_hour.keys()) == set(range(24))


def test_runs_per_hour_every_minute():
    result = profile(_expr("* * * * *"), ref=REF, window_hours=1)
    assert result.runs_per_hour[0] == 60


def test_runs_per_hour_specific_hour():
    result = profile(_expr("0 9 * * *"), ref=REF, window_hours=24)
    assert result.runs_per_hour[9] == 1
    assert result.runs_per_hour[10] == 0


# ---------------------------------------------------------------------------
# busiest / quietest
# ---------------------------------------------------------------------------

def test_busiest_hour_for_hourly():
    # every hour fires once — all equal, so busiest == quietest is fine
    result = profile(_expr("0 * * * *"), ref=REF, window_hours=24)
    assert result.runs_per_hour[result.busiest_hour] >= 1


def test_busiest_hour_for_specific_hour():
    result = profile(_expr("* 3 * * *"), ref=REF, window_hours=24)
    assert result.busiest_hour == 3


# ---------------------------------------------------------------------------
# error handling
# ---------------------------------------------------------------------------

def test_window_hours_less_than_one_raises():
    with pytest.raises(ValueError):
        profile(_expr("* * * * *"), ref=REF, window_hours=0)
