"""Tests for cronlens.summarizer."""

from __future__ import annotations

from datetime import datetime

import pytest

from cronlens.parser import CronExpression
from cronlens.summarizer import RunStats, summarize


REF = datetime(2024, 1, 15, 12, 0)


@pytest.fixture()
def every_minute() -> CronExpression:
    return CronExpression("* * * * *")


@pytest.fixture()
def hourly() -> CronExpression:
    return CronExpression("0 * * * *")


@pytest.fixture()
def daily() -> CronExpression:
    return CronExpression("0 9 * * *")


def test_summarize_returns_run_stats(every_minute):
    result = summarize(every_minute, ref=REF, sample=10)
    assert isinstance(result, RunStats)


def test_sample_size_stored(every_minute):
    result = summarize(every_minute, ref=REF, sample=20)
    assert result.sample_size == 20


def test_every_minute_gaps_are_60s(every_minute):
    result = summarize(every_minute, ref=REF, sample=10)
    assert result.min_gap_seconds == pytest.approx(60.0)
    assert result.max_gap_seconds == pytest.approx(60.0)
    assert result.avg_gap_seconds == pytest.approx(60.0)


def test_every_minute_runs_per_hour(every_minute):
    result = summarize(every_minute, ref=REF, sample=10)
    assert result.runs_per_hour == pytest.approx(60.0)


def test_every_minute_runs_per_day(every_minute):
    result = summarize(every_minute, ref=REF, sample=10)
    assert result.runs_per_day == pytest.approx(1440.0)


def test_hourly_avg_gap(hourly):
    result = summarize(hourly, ref=REF, sample=5)
    assert result.avg_gap_seconds == pytest.approx(3600.0)


def test_next_run_is_datetime(every_minute):
    result = summarize(every_minute, ref=REF, sample=5)
    assert isinstance(result.next_run, datetime)


def test_next_run_after_ref(every_minute):
    result = summarize(every_minute, ref=REF, sample=5)
    assert result.next_run > REF


def test_intervals_length(every_minute):
    result = summarize(every_minute, ref=REF, sample=10)
    assert len(result.intervals) == 9  # n runs → n-1 intervals


def test_sample_less_than_2_raises(every_minute):
    with pytest.raises(ValueError, match="sample must be >= 2"):
        summarize(every_minute, ref=REF, sample=1)


def test_str_contains_expression(every_minute):
    result = summarize(every_minute, ref=REF, sample=5)
    assert "* * * * *" in str(result)


def test_str_contains_next_run(every_minute):
    result = summarize(every_minute, ref=REF, sample=5)
    assert str(result.next_run.year) in str(result)


def test_min_gap_timedelta(every_minute):
    from datetime import timedelta
    result = summarize(every_minute, ref=REF, sample=5)
    assert result.min_gap == timedelta(seconds=60)


def test_daily_runs_per_day(daily):
    result = summarize(daily, ref=REF, sample=4)
    assert result.runs_per_day == pytest.approx(1.0)
