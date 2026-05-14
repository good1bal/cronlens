"""Tests for cronlens.classifier."""

import pytest
from cronlens.parser import CronExpression
from cronlens.classifier import (
    classify,
    ClassifyResult,
    EVERY_MINUTE,
    HOURLY,
    DAILY,
    WEEKLY,
    MONTHLY,
    YEARLY,
    CUSTOM,
)


def _expr(s: str) -> CronExpression:
    return CronExpression(s)


def test_classify_returns_classify_result():
    result = classify(_expr("* * * * *"))
    assert isinstance(result, ClassifyResult)


def test_every_minute():
    assert classify(_expr("* * * * *")).category == EVERY_MINUTE


def test_hourly_at_fixed_minute():
    assert classify(_expr("30 * * * *")).category == HOURLY


def test_daily_at_fixed_time():
    assert classify(_expr("0 9 * * *")).category == DAILY


def test_weekly_specific_weekday():
    assert classify(_expr("0 9 * * 1")).category == WEEKLY


def test_weekly_multiple_weekdays():
    assert classify(_expr("0 8 * * 1,3,5")).category == WEEKLY


def test_monthly_specific_dom():
    assert classify(_expr("0 0 1 * *")).category == MONTHLY


def test_yearly_specific_month_and_dom():
    assert classify(_expr("0 0 1 1 *")).category == YEARLY


def test_custom_complex_expression():
    assert classify(_expr("*/15 9-17 * * 1-5")).category == CUSTOM


def test_str_contains_category():
    result = classify(_expr("* * * * *"))
    assert EVERY_MINUTE in str(result)


def test_str_contains_expression():
    result = classify(_expr("0 9 * * *"))
    assert "0 9 * * *" in str(result)


def test_description_is_non_empty():
    result = classify(_expr("0 9 * * *"))
    assert result.description


def test_every_minute_description():
    result = classify(_expr("* * * * *"))
    assert "every minute" in result.description.lower()
