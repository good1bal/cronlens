"""Tests for cronlens.history."""

from datetime import datetime

import pytest

from cronlens.parser import CronExpression
from cronlens.history import prev_runs, iter_prev_runs


REF = datetime(2024, 6, 15, 12, 30, 0)  # Saturday, 12:30


def test_prev_runs_returns_n_results():
    expr = CronExpression("* * * * *")
    results = prev_runs(expr, n=5, ref=REF)
    assert len(results) == 5


def test_prev_runs_are_before_ref():
    expr = CronExpression("* * * * *")
    results = prev_runs(expr, n=10, ref=REF)
    for dt in results:
        assert dt < REF


def test_prev_runs_descending_order():
    expr = CronExpression("* * * * *")
    results = prev_runs(expr, n=5, ref=REF)
    for a, b in zip(results, results[1:]):
        assert a > b


def test_every_minute_consecutive():
    expr = CronExpression("* * * * *")
    results = prev_runs(expr, n=3, ref=REF)
    assert results[0] == datetime(2024, 6, 15, 12, 29)
    assert results[1] == datetime(2024, 6, 15, 12, 28)
    assert results[2] == datetime(2024, 6, 15, 12, 27)


def test_specific_minute_and_hour():
    # Run at 09:15 every day
    expr = CronExpression("15 9 * * *")
    ref = datetime(2024, 6, 15, 10, 0)
    results = prev_runs(expr, n=3, ref=ref)
    for dt in results:
        assert dt.minute == 15
        assert dt.hour == 9


def test_weekday_filter():
    # Run every minute on Monday (weekday=0)
    expr = CronExpression("* * * * 1")
    # REF is Saturday (weekday=5); look back to find Mondays
    results = prev_runs(expr, n=5, ref=REF)
    for dt in results:
        assert dt.weekday() == 0


def test_n_less_than_one_raises():
    expr = CronExpression("* * * * *")
    with pytest.raises(ValueError):
        prev_runs(expr, n=0, ref=REF)


def test_iter_prev_runs_is_infinite():
    expr = CronExpression("* * * * *")
    gen = iter_prev_runs(expr, ref=REF)
    results = [next(gen) for _ in range(100)]
    assert len(results) == 100
