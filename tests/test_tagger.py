"""Tests for cronlens.tagger."""

import pytest

from cronlens.parser import CronExpression
from cronlens.tagger import TagResult, tag


def _expr(s: str) -> CronExpression:
    return CronExpression(s)


# ---------------------------------------------------------------------------
# TagResult helpers
# ---------------------------------------------------------------------------

def test_tag_result_str_no_tags():
    result = TagResult(expression="* * * * *", tags=[])
    assert "no tags" in str(result)


def test_tag_result_str_with_tags():
    result = TagResult(expression="0 * * * *", tags=["hourly"])
    assert "hourly" in str(result)


# ---------------------------------------------------------------------------
# every-minute
# ---------------------------------------------------------------------------

def test_every_minute_tagged():
    result = tag(_expr("* * * * *"))
    assert "every-minute" in result.tags


# ---------------------------------------------------------------------------
# hourly
# ---------------------------------------------------------------------------

def test_hourly_tagged():
    result = tag(_expr("0 * * * *"))
    assert "hourly" in result.tags


def test_hourly_not_every_minute():
    result = tag(_expr("0 * * * *"))
    assert "every-minute" not in result.tags


# ---------------------------------------------------------------------------
# daily
# ---------------------------------------------------------------------------

def test_daily_tagged():
    result = tag(_expr("30 6 * * *"))
    assert "daily" in result.tags


def test_daily_not_weekly():
    result = tag(_expr("30 6 * * *"))
    assert "weekly" not in result.tags


# ---------------------------------------------------------------------------
# weekly / weekday-only
# ---------------------------------------------------------------------------

def test_weekly_tagged():
    result = tag(_expr("0 9 * * 1"))
    assert "weekly" in result.tags


def test_weekday_only_tagged_with_weekly():
    result = tag(_expr("0 9 * * 1"))
    assert "weekday-only" in result.tags


def test_weekday_only_without_weekly():
    # specific dom AND specific dow — weekday-only but not purely weekly
    result = tag(_expr("0 9 15 * 1"))
    assert "weekday-only" in result.tags


# ---------------------------------------------------------------------------
# monthly
# ---------------------------------------------------------------------------

def test_monthly_tagged():
    result = tag(_expr("0 0 1 * *"))
    assert "monthly" in result.tags


# ---------------------------------------------------------------------------
# month-restricted
# ---------------------------------------------------------------------------

def test_month_restricted_tagged():
    result = tag(_expr("0 0 * 12 *"))
    assert "month-restricted" in result.tags


def test_month_restricted_combined_with_daily():
    result = tag(_expr("30 8 * 6 *"))
    assert "month-restricted" in result.tags
    assert "daily" in result.tags


# ---------------------------------------------------------------------------
# multiple-times-per-day
# ---------------------------------------------------------------------------

def test_multiple_times_per_day_tagged():
    result = tag(_expr("0 6,12,18 * * *"))
    assert "multiple-times-per-day" in result.tags


def test_multiple_times_per_day_not_daily():
    result = tag(_expr("0 6,12 * * *"))
    assert "daily" not in result.tags
