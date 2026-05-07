"""Tests for the CronExpression parser."""

import pytest
from cronlens.parser import CronExpression, CronParseError


# ---------------------------------------------------------------------------
# Valid expressions – construction should not raise
# ---------------------------------------------------------------------------

class TestValidExpressions:
    def test_every_minute(self):
        expr = CronExpression("* * * * *")
        assert expr.minutes == list(range(60))
        assert expr.hours == list(range(24))
        assert expr.days == list(range(1, 32))
        assert expr.months == list(range(1, 13))
        assert expr.weekdays == list(range(7))

    def test_specific_values(self):
        expr = CronExpression("30 6 15 3 2")
        assert expr.minutes == [30]
        assert expr.hours == [6]
        assert expr.days == [15]
        assert expr.months == [3]
        assert expr.weekdays == [2]

    def test_comma_list(self):
        expr = CronExpression("0,15,30,45 * * * *")
        assert expr.minutes == [0, 15, 30, 45]

    def test_range(self):
        expr = CronExpression("0-5 * * * *")
        assert expr.minutes == [0, 1, 2, 3, 4, 5]

    def test_step_on_wildcard(self):
        expr = CronExpression("*/15 * * * *")
        assert expr.minutes == [0, 15, 30, 45]

    def test_step_on_range(self):
        expr = CronExpression("0-30/10 * * * *")
        assert expr.minutes == [0, 10, 20, 30]

    def test_mixed_field(self):
        """Comma-separated mix of ranges and literals."""
        expr = CronExpression("1,5-7,10 * * * *")
        assert expr.minutes == [1, 5, 6, 7, 10]

    def test_hour_range(self):
        expr = CronExpression("0 9-17 * * *")
        assert expr.hours == list(range(9, 18))

    def test_weekday_zero_and_seven_both_sunday(self):
        """Both 0 and 7 should map to Sunday (0)."""
        expr = CronExpression("0 0 * * 7")
        assert 0 in expr.weekdays

    def test_repr_round_trip(self):
        raw = "*/5 0 1 1 *"
        expr = CronExpression(raw)
        assert raw in repr(expr)


# ---------------------------------------------------------------------------
# Invalid expressions – should raise CronParseError
# ---------------------------------------------------------------------------

class TestInvalidExpressions:
    def test_too_few_fields(self):
        with pytest.raises(CronParseError, match="5 fields"):
            CronExpression("* * * *")

    def test_too_many_fields(self):
        with pytest.raises(CronParseError, match="5 fields"):
            CronExpression("* * * * * *")

    def test_minute_out_of_range(self):
        with pytest.raises(CronParseError):
            CronExpression("60 * * * *")

    def test_hour_out_of_range(self):
        with pytest.raises(CronParseError):
            CronExpression("0 24 * * *")

    def test_day_out_of_range(self):
        with pytest.raises(CronParseError):
            CronExpression("0 0 32 * *")

    def test_month_out_of_range(self):
        with pytest.raises(CronParseError):
            CronExpression("0 0 1 13 *")

    def test_weekday_out_of_range(self):
        with pytest.raises(CronParseError):
            CronExpression("0 0 * * 8")

    def test_invalid_step_zero(self):
        """A step of 0 is meaningless and should be rejected."""
        with pytest.raises(CronParseError):
            CronExpression("*/0 * * * *")

    def test_non_numeric_field(self):
        with pytest.raises(CronParseError):
            CronExpression("abc * * * *")

    def test_empty_string(self):
        with pytest.raises(CronParseError):
            CronExpression("")

    def test_inverted_range(self):
        """Start greater than end in a range should raise."""
        with pytest.raises(CronParseError):
            CronExpression("10-5 * * * *")
