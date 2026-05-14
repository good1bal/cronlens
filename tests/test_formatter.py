"""Tests for cronlens.formatter."""

import pytest

from cronlens.parser import CronExpression
from cronlens.formatter import (
    format_field_table,
    format_summary,
    format_full,
    format_merge_result,
)
from cronlens.merger import merge


@pytest.fixture
def every_minute():
    return CronExpression("* * * * *")


@pytest.fixture
def specific_expr():
    return CronExpression("30 9 * * 1-5")


# ---------------------------------------------------------------------------
# format_summary
# ---------------------------------------------------------------------------

class TestFormatSummary:
    def test_contains_expression(self, specific_expr):
        out = format_summary(specific_expr)
        assert str(specific_expr) in out

    def test_contains_meaning_label(self, specific_expr):
        out = format_summary(specific_expr)
        assert "Meaning" in out

    def test_every_minute_meaning(self, every_minute):
        out = format_summary(every_minute)
        assert "every minute" in out.lower()


# ---------------------------------------------------------------------------
# format_field_table
# ---------------------------------------------------------------------------

class TestFormatFieldTable:
    def test_contains_all_field_labels(self, every_minute):
        out = format_field_table(every_minute)
        for label in ["Minute", "Hour", "Day", "Month", "Weekday"]:
            assert label in out

    def test_contains_wildcard_for_every_minute(self, every_minute):
        out = format_field_table(every_minute)
        assert "*" in out

    def test_contains_specific_values(self, specific_expr):
        out = format_field_table(specific_expr)
        assert "30" in out
        assert "9" in out
        assert "1-5" in out

    def test_row_count(self, every_minute):
        out = format_field_table(every_minute)
        # header + separator + 5 data rows
        assert len(out.strip().splitlines()) == 7


# ---------------------------------------------------------------------------
# format_full
# ---------------------------------------------------------------------------

def test_format_full_contains_summary(specific_expr):
    out = format_full(specific_expr)
    assert "Meaning" in out
    assert str(specific_expr) in out


def test_format_full_contains_table(specific_expr):
    out = format_full(specific_expr)
    assert "Minute" in out
    assert "Hour" in out


# ---------------------------------------------------------------------------
# format_merge_result
# ---------------------------------------------------------------------------

def test_format_merge_result_contains_header():
    a = CronExpression("0 12 * * *")
    b = CronExpression("0 0 * * *")
    result = merge(a, b)
    out = format_merge_result(result)
    assert "Merge Result" in out


def test_format_merge_result_lossless_marker():
    a = CronExpression("0 12 * * *")
    b = CronExpression("0 12 * * *")
    result = merge(a, b)
    out = format_merge_result(result)
    assert "lossless" in out.lower()


def test_format_merge_result_lossy_warning():
    a = CronExpression("* * * * *")
    b = CronExpression("0 12 * * *")
    result = merge(a, b)
    out = format_merge_result(result)
    assert "Lossy" in out or "lossy" in out
