"""Tests for cronlens.humanizer."""

import pytest

from cronlens.parser import CronExpression
from cronlens.humanizer import humanize


def _expr(s: str) -> CronExpression:
    return CronExpression(s)


def test_every_minute():
    assert humanize(_expr("* * * * *")) == "every minute"


def test_specific_time():
    result = humanize(_expr("30 9 * * *"))
    assert "09:30" in result


def test_multiple_hours():
    result = humanize(_expr("0 9,17 * * *"))
    assert "09:00" in result
    assert "17:00" in result


def test_every_minute_of_hour():
    result = humanize(_expr("* 6 * * *"))
    assert "every minute" in result
    assert "6" in result


def test_at_minute_of_every_hour():
    result = humanize(_expr("15 * * * *"))
    assert "15" in result
    assert "every hour" in result


def test_specific_weekday():
    result = humanize(_expr("0 9 * * 1"))
    assert "Monday" in result


def test_multiple_weekdays():
    result = humanize(_expr("0 9 * * 1,3,5"))
    assert "Monday" in result
    assert "Wednesday" in result
    assert "Friday" in result


def test_specific_month():
    result = humanize(_expr("0 0 1 12 *"))
    assert "December" in result


def test_specific_day_of_month():
    result = humanize(_expr("0 8 15 * *"))
    assert "15th" in result


def test_day_and_weekday_both_set():
    result = humanize(_expr("0 9 1 * 1"))
    assert "1st" in result
    assert "Monday" in result


def test_multiple_months():
    result = humanize(_expr("0 0 1 3,6,9,12 *"))
    assert "March" in result
    assert "June" in result
    assert "September" in result
    assert "December" in result


def test_ordinal_second():
    result = humanize(_expr("0 0 2 * *"))
    assert "2nd" in result


def test_ordinal_third():
    result = humanize(_expr("0 0 3 * *"))
    assert "3rd" in result


def test_returns_string():
    assert isinstance(humanize(_expr("*/5 * * * *")), str)
