"""Tests for cronlens.narrower."""
from datetime import datetime, timedelta

import pytest

from cronlens.narrower import NarrowResult, narrow


REF = datetime(2024, 6, 1, 12, 0, 0)


def _narrow(expr: str, hours: int = 1, start: datetime = REF) -> NarrowResult:
    end = start + timedelta(hours=hours)
    return narrow(expr, start=start, end=end)


# ---------------------------------------------------------------------------
# Basic return-type checks
# ---------------------------------------------------------------------------

def test_narrow_returns_narrow_result():
    result = _narrow("* * * * *")
    assert isinstance(result, NarrowResult)


def test_narrow_stores_expression():
    result = _narrow("0 * * * *")
    assert result.expression == "0 * * * *"


def test_narrow_stores_start_and_end():
    end = REF + timedelta(hours=2)
    result = narrow("* * * * *", start=REF, end=end)
    assert result.start == REF
    assert result.end == end


# ---------------------------------------------------------------------------
# Run counts
# ---------------------------------------------------------------------------

def test_every_minute_one_hour_gives_60_runs():
    result = _narrow("* * * * *", hours=1)
    assert result.count == 60


def test_hourly_expression_gives_one_run_in_one_hour():
    # "0 * * * *" fires at :00 of each hour
    start = datetime(2024, 6, 1, 12, 0)
    end = start + timedelta(hours=1)
    result = narrow("0 * * * *", start=start, end=end)
    assert result.count == 1


def test_daily_expression_gives_one_run_in_24_hours():
    start = datetime(2024, 6, 1, 0, 0)
    end = start + timedelta(hours=24)
    result = narrow("0 9 * * *", start=start, end=end)
    assert result.count == 1


def test_no_match_in_window_gives_empty_runs():
    # Expression fires at 03:00; window is 12:00–13:00
    result = _narrow("0 3 * * *", hours=1)
    assert result.count == 0
    assert result.runs == []


# ---------------------------------------------------------------------------
# first_run / last_run helpers
# ---------------------------------------------------------------------------

def test_first_run_is_none_when_no_runs():
    result = _narrow("0 3 * * *", hours=1)
    assert result.first_run is None


def test_last_run_is_none_when_no_runs():
    result = _narrow("0 3 * * *", hours=1)
    assert result.last_run is None


def test_first_and_last_run_populated():
    result = _narrow("* * * * *", hours=1)
    assert result.first_run is not None
    assert result.last_run is not None
    assert result.first_run < result.last_run


# ---------------------------------------------------------------------------
# Boundary / error cases
# ---------------------------------------------------------------------------

def test_end_before_start_raises_value_error():
    with pytest.raises(ValueError):
        narrow("* * * * *", start=REF, end=REF - timedelta(minutes=1))


def test_end_equal_to_start_raises_value_error():
    with pytest.raises(ValueError):
        narrow("* * * * *", start=REF, end=REF)


def test_invalid_expression_raises_value_error():
    with pytest.raises(ValueError):
        _narrow("not a cron")


# ---------------------------------------------------------------------------
# __str__ smoke test
# ---------------------------------------------------------------------------

def test_str_contains_expression():
    result = _narrow("* * * * *")
    assert "* * * * *" in str(result)


def test_str_contains_run_count():
    result = _narrow("* * * * *")
    assert str(result.count) in str(result)
