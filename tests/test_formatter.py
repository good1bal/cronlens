"""Tests for cronlens.formatter."""

import pytest

from cronlens.parser import CronExpression
from cronlens.formatter import format_summary, format_field_table, format_full


@pytest.fixture
def every_minute():
    return CronExpression("* * * * *")


@pytest.fixture
def specific_expr():
    return CronExpression("30 9 * * 1-5")


class TestFormatSummary:
    def test_contains_expression(self, every_minute):
        result = format_summary(every_minute, color=False)
        assert "* * * * *" in result

    def test_contains_meaning_label(self, every_minute):
        result = format_summary(every_minute, color=False)
        assert "Meaning" in result

    def test_no_color_no_ansi(self, specific_expr):
        result = format_summary(specific_expr, color=False)
        assert "\033[" not in result

    def test_color_contains_ansi(self, specific_expr):
        result = format_summary(specific_expr, color=True)
        assert "\033[" in result

    def test_specific_expr_contains_raw(self, specific_expr):
        result = format_summary(specific_expr, color=False)
        assert "30 9 * * 1-5" in result


class TestFormatFieldTable:
    def test_contains_all_field_labels(self, every_minute):
        result = format_field_table(every_minute, color=False)
        for label in ["Minute", "Hour", "Day (month)", "Month", "Day (week)"]:
            assert label in result

    def test_contains_field_values(self, specific_expr):
        result = format_field_table(specific_expr, color=False)
        assert "30" in result
        assert "9" in result
        assert "1-5" in result

    def test_no_color_no_ansi(self, every_minute):
        result = format_field_table(every_minute, color=False)
        assert "\033[" not in result

    def test_color_contains_ansi(self, every_minute):
        result = format_field_table(every_minute, color=True)
        assert "\033[" in result

    def test_table_structure(self, every_minute):
        result = format_field_table(every_minute, color=False)
        assert result.startswith("+")
        assert result.count("+--") >= 2


class TestFormatFull:
    def test_contains_summary_and_table(self, specific_expr):
        result = format_full(specific_expr, color=False)
        assert "Expression" in result
        assert "Minute" in result

    def test_no_color(self, specific_expr):
        result = format_full(specific_expr, color=False)
        assert "\033[" not in result

    def test_color(self, specific_expr):
        result = format_full(specific_expr, color=True)
        assert "\033[" in result
