"""Tests for cronlens.explainer."""

import pytest
from cronlens.parser import CronExpression
from cronlens.explainer import explain


def test_every_minute():
    expr = CronExpression("* * * * *")
    assert explain(expr) == "Runs every minute."


def test_specific_minute_and_hour():
    expr = CronExpression("30 9 * * *")
    result = explain(expr)
    assert "minute 30" in result
    assert "hour 9" in result


def test_every_hour_at_minute_zero():
    expr = CronExpression("0 * * * *")
    result = explain(expr)
    assert "minute 0" in result
    assert "hour" not in result or "every hour" not in result


def test_specific_weekdays():
    expr = CronExpression("0 9 * * 1,5")
    result = explain(expr)
    assert "Monday" in result
    assert "Friday" in result


def test_specific_months():
    expr = CronExpression("0 0 1 3,6 *")
    result = explain(expr)
    assert "March" in result
    assert "June" in result


def test_single_weekday():
    expr = CronExpression("0 12 * * 3")
    result = explain(expr)
    assert "Wednesday" in result


def test_dom_included():
    expr = CronExpression("0 0 15 * *")
    result = explain(expr)
    assert "day-of-month 15" in result


def test_all_fields_specified():
    expr = CronExpression("5 4 1 1 0")
    result = explain(expr)
    assert "minute 5" in result
    assert "hour 4" in result
    assert "day-of-month 1" in result
    assert "January" in result
    assert "Sunday" in result


def test_multiple_minutes():
    expr = CronExpression("0,30 * * * *")
    result = explain(expr)
    assert "0" in result
    assert "30" in result


def test_returns_string():
    expr = CronExpression("*/5 * * * *")
    result = explain(expr)
    assert isinstance(result, str)
    assert result.endswith(".")
