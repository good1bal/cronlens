"""Tests for cronlens.merger."""

import pytest

from cronlens.merger import merge, _merge_field
from cronlens.parser import CronExpression


# ---------------------------------------------------------------------------
# _merge_field unit tests
# ---------------------------------------------------------------------------

def test_merge_field_both_wildcard():
    assert _merge_field("*", "*") == "*"


def test_merge_field_one_wildcard():
    assert _merge_field("5", "*") == "*"
    assert _merge_field("*", "10") == "*"


def test_merge_field_distinct_values():
    result = _merge_field("5", "10")
    assert result == "5,10"


def test_merge_field_overlapping_values():
    result = _merge_field("5,10", "10,15")
    assert "5" in result
    assert "10" in result
    assert "15" in result
    assert result.count("10") == 1  # no duplicates


# ---------------------------------------------------------------------------
# merge() integration tests
# ---------------------------------------------------------------------------

@pytest.fixture
def every_minute():
    return CronExpression("* * * * *")


@pytest.fixture
def at_5_and_10():
    return CronExpression("5,10 * * * *")


@pytest.fixture
def at_noon():
    return CronExpression("0 12 * * *")


@pytest.fixture
def at_midnight():
    return CronExpression("0 0 * * *")


def test_merge_returns_merge_result(at_noon, at_midnight):
    result = merge(at_noon, at_midnight)
    assert result.merged is not None


def test_merge_identical_is_lossless(at_noon):
    result = merge(at_noon, at_noon)
    assert result.is_lossless()


def test_merge_with_wildcard_is_lossy(every_minute, at_noon):
    result = merge(every_minute, at_noon)
    # hour field: "*" vs "12" → wildcard wins, lossy
    assert not result.is_lossless()
    assert "hour" in result.lossy_fields or "minute" in result.lossy_fields


def test_merge_combined_minutes(at_5_and_10, at_midnight):
    result = merge(at_5_and_10, at_midnight)
    assert "0" in result.merged.minute
    assert "5" in result.merged.minute
    assert "10" in result.merged.minute


def test_merge_summary_contains_both_expressions(at_noon, at_midnight):
    result = merge(at_noon, at_midnight)
    summary = result.summary()
    assert str(at_noon) in summary
    assert str(at_midnight) in summary


def test_merge_summary_lossless_message(at_noon, at_noon_copy=None):
    a = CronExpression("0 12 * * *")
    b = CronExpression("0 12 * * *")
    result = merge(a, b)
    assert "lossless" in result.summary()


def test_merge_summary_lossy_message(every_minute, at_noon):
    result = merge(every_minute, at_noon)
    assert "wildcard expansion" in result.summary()
