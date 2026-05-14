"""Tests for cronlens.grouper."""

import pytest

from cronlens.grouper import GroupResult, group


EVERY_MINUTE = "* * * * *"
HOURLY = "0 * * * *"
DAILY = "0 9 * * *"
WEEKLY = "0 9 * * 1"
MONTHLY = "0 9 1 * *"
INVALID = "not-a-cron"


def test_group_returns_group_result():
    result = group([EVERY_MINUTE])
    assert isinstance(result, GroupResult)


def test_every_minute_in_every_minute_category():
    result = group([EVERY_MINUTE])
    assert "every-minute" in result.groups
    assert EVERY_MINUTE in result.groups["every-minute"]


def test_hourly_expression_grouped_correctly():
    result = group([HOURLY])
    assert "hourly" in result.groups
    assert HOURLY in result.groups["hourly"]


def test_daily_expression_grouped_correctly():
    result = group([DAILY])
    assert "daily" in result.groups
    assert DAILY in result.groups["daily"]


def test_invalid_expression_goes_to_invalid_list():
    result = group([INVALID])
    assert INVALID in result.invalid
    assert not result.groups


def test_mixed_expressions_split_correctly():
    result = group([EVERY_MINUTE, HOURLY, DAILY, INVALID])
    assert EVERY_MINUTE in result.groups.get("every-minute", [])
    assert HOURLY in result.groups.get("hourly", [])
    assert DAILY in result.groups.get("daily", [])
    assert INVALID in result.invalid


def test_category_names_sorted():
    result = group([EVERY_MINUTE, HOURLY, DAILY])
    names = result.category_names
    assert names == sorted(names)


def test_expressions_for_returns_correct_list():
    result = group([HOURLY, DAILY])
    assert HOURLY in result.expressions_for("hourly")


def test_expressions_for_missing_category_returns_empty():
    result = group([HOURLY])
    assert result.expressions_for("nonexistent") == []


def test_empty_input_returns_empty_result():
    result = group([])
    assert result.groups == {}
    assert result.invalid == []


def test_multiple_exprs_same_category():
    result = group(["0 8 * * *", "30 10 * * *"])
    daily = result.expressions_for("daily")
    assert len(daily) == 2


def test_weekly_expression_grouped():
    result = group([WEEKLY])
    assert "weekly" in result.groups


def test_monthly_expression_grouped():
    result = group([MONTHLY])
    assert "monthly" in result.groups
