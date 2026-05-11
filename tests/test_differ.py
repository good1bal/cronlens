"""Tests for cronlens.differ."""

import pytest

from cronlens.differ import diff_expressions, CronDiff, FieldDiff


def test_identical_expressions_no_diffs():
    result = diff_expressions("* * * * *", "* * * * *")
    assert result.is_identical
    assert result.changed_fields == []


def test_identical_summary_message():
    result = diff_expressions("0 * * * *", "0 * * * *")
    assert "identical" in result.summary()


def test_single_field_difference():
    result = diff_expressions("0 * * * *", "5 * * * *")
    assert not result.is_identical
    assert len(result.changed_fields) == 1
    assert result.changed_fields[0].field == "minute"
    assert result.changed_fields[0].left == "0"
    assert result.changed_fields[0].right == "5"


def test_multiple_field_differences():
    result = diff_expressions("0 6 * * 1", "30 12 * * 5")
    fields = {fd.field for fd in result.changed_fields}
    assert "minute" in fields
    assert "hour" in fields
    assert "day_of_week" in fields
    assert len(result.changed_fields) == 3


def test_summary_contains_field_names():
    result = diff_expressions("0 6 1 * *", "0 9 15 * *")
    summary = result.summary()
    assert "hour" in summary
    assert "day_of_month" in summary


def test_summary_contains_expressions():
    left, right = "*/5 * * * *", "*/10 * * * *"
    result = diff_expressions(left, right)
    summary = result.summary()
    assert left in summary
    assert right in summary


def test_field_diff_str():
    fd = FieldDiff(field="minute", left="0", right="30")
    text = str(fd)
    assert "minute" in text
    assert "0" in text
    assert "30" in text
    assert "→" in text


def test_range_vs_step_difference():
    result = diff_expressions("1-5 * * * *", "*/5 * * * *")
    assert not result.is_identical
    assert result.changed_fields[0].field == "minute"


def test_all_fields_identical_comma_list():
    expr = "1,2,3 4,5 * 6,7 1,2"
    result = diff_expressions(expr, expr)
    assert result.is_identical
