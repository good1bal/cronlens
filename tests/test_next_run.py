"""Tests for cronlens.next_run."""

from __future__ import annotations

from datetime import datetime

import pytest

from cronlens.next_run import next_runs
from cronlens.parser import CronExpression


_ANCHOR = datetime(2024, 3, 4, 10, 0, 0)  # Monday 10:00


def test_every_minute_returns_n_results():
    expr = CronExpression("* * * * *")
    runs = next_runs(expr, n=5, after=_ANCHOR)
    assert len(runs) == 5


def test_every_minute_consecutive():
    from datetime import timedelta
    expr = CronExpression("* * * * *")
    runs = next_runs(expr, n=3, after=_ANCHOR)
    for i in range(1, len(runs)):
        assert runs[i] - runs[i - 1] == timedelta(minutes=1)


def test_specific_minute_and_hour():
    expr = CronExpression("30 14 * * *")
    runs = next_runs(expr, n=1, after=_ANCHOR)
    assert runs[0].hour == 14
    assert runs[0].minute == 30


def test_weekday_filter():
    # Only Saturdays (weekday=5)
    expr = CronExpression("0 12 * * 6")
    runs = next_runs(expr, n=3, after=_ANCHOR)
    for dt in runs:
        assert dt.weekday() == 5  # Saturday


def test_n_less_than_one_raises():
    expr = CronExpression("* * * * *")
    with pytest.raises(ValueError, match="n must be"):
        next_runs(expr, n=0)


def test_monthly_expression():
    # 1st of every month at midnight
    expr = CronExpression("0 0 1 * *")
    runs = next_runs(expr, n=2, after=_ANCHOR)
    for dt in runs:
        assert dt.day == 1
        assert dt.hour == 0
        assert dt.minute == 0
