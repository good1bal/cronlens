"""Tests for cronlens.forecaster."""

from __future__ import annotations

from datetime import datetime

import pytest

from cronlens.parser import CronExpression
from cronlens.forecaster import ForecastResult, forecast


REF = datetime(2024, 6, 1, 0, 0, 0)


def _expr(s: str) -> CronExpression:
    return CronExpression(s)


# ---------------------------------------------------------------------------
# forecast() return type
# ---------------------------------------------------------------------------

def test_forecast_returns_forecast_result():
    result = forecast(_expr("* * * * *"), window_hours=1, ref=REF)
    assert isinstance(result, ForecastResult)


def test_forecast_stores_expression():
    result = forecast(_expr("* * * * *"), window_hours=1, ref=REF)
    assert "*" in result.expression


def test_forecast_stores_window_hours():
    result = forecast(_expr("* * * * *"), window_hours=3, ref=REF)
    assert result.window_hours == 3


# ---------------------------------------------------------------------------
# run counts
# ---------------------------------------------------------------------------

def test_every_minute_one_hour_gives_60_runs():
    result = forecast(_expr("* * * * *"), window_hours=1, ref=REF)
    assert result.count == 60


def test_hourly_one_day_gives_24_runs():
    result = forecast(_expr("0 * * * *"), window_hours=24, ref=REF)
    assert result.count == 24


def test_daily_midnight_one_week_gives_7_runs():
    result = forecast(_expr("0 0 * * *"), window_hours=24 * 7, ref=REF)
    assert result.count == 7


def test_specific_time_outside_window_gives_zero():
    # fires at 23:45 but window is only 1 hour from midnight
    result = forecast(_expr("45 23 * * *"), window_hours=1, ref=REF)
    assert result.count == 0


# ---------------------------------------------------------------------------
# runs_per_hour
# ---------------------------------------------------------------------------

def test_runs_per_hour_every_minute():
    result = forecast(_expr("* * * * *"), window_hours=2, ref=REF)
    assert result.runs_per_hour == 60.0


def test_runs_per_hour_zero_when_no_runs():
    result = forecast(_expr("45 23 * * *"), window_hours=1, ref=REF)
    assert result.runs_per_hour == 0.0


# ---------------------------------------------------------------------------
# first / last run
# ---------------------------------------------------------------------------

def test_first_run_is_none_when_no_runs():
    result = forecast(_expr("45 23 * * *"), window_hours=1, ref=REF)
    assert result.first_run is None


def test_first_run_is_datetime_when_runs_exist():
    result = forecast(_expr("* * * * *"), window_hours=1, ref=REF)
    assert isinstance(result.first_run, datetime)


def test_last_run_is_after_first_run():
    result = forecast(_expr("* * * * *"), window_hours=1, ref=REF)
    assert result.last_run >= result.first_run  # type: ignore[operator]


# ---------------------------------------------------------------------------
# __str__
# ---------------------------------------------------------------------------

def test_str_contains_expression():
    result = forecast(_expr("0 * * * *"), window_hours=1, ref=REF)
    assert result.expression in str(result)


def test_str_contains_total_runs():
    result = forecast(_expr("0 * * * *"), window_hours=24, ref=REF)
    assert str(result.count) in str(result)


def test_str_contains_window_hours():
    result = forecast(_expr("* * * * *"), window_hours=6, ref=REF)
    assert "6" in str(result)


# ---------------------------------------------------------------------------
# invalid window
# ---------------------------------------------------------------------------

def test_window_hours_less_than_one_raises():
    with pytest.raises(ValueError):
        forecast(_expr("* * * * *"), window_hours=0, ref=REF)
