"""Tests for cronlens.overlapper."""

from datetime import datetime

import pytest

from cronlens.parser import CronExpression
from cronlens.overlapper import OverlapResult, find_overlaps


REF = datetime(2024, 1, 15, 12, 0, 0)


def _expr(s: str) -> CronExpression:
    return CronExpression(s)


# ---------------------------------------------------------------------------
# find_overlaps return type
# ---------------------------------------------------------------------------

def test_find_overlaps_returns_overlap_result():
    result = find_overlaps(_expr("* * * * *"), _expr("* * * * *"), ref=REF, window_hours=1)
    assert isinstance(result, OverlapResult)


def test_identical_every_minute_has_full_overlap():
    result = find_overlaps(_expr("* * * * *"), _expr("* * * * *"), ref=REF, window_hours=1)
    assert result.count == 60
    assert result.has_overlap is True


def test_disjoint_hours_no_overlap():
    # runs only at 02:00, 03:00 vs runs only at 10:00, 11:00 — within 1h window starting noon
    result = find_overlaps(
        _expr("0 13 * * *"),
        _expr("0 14 * * *"),
        ref=REF,
        window_hours=1,
    )
    assert result.count == 0
    assert result.has_overlap is False


def test_same_specific_time_overlaps():
    result = find_overlaps(
        _expr("30 13 * * *"),
        _expr("30 13 * * *"),
        ref=REF,
        window_hours=2,
    )
    assert result.count == 1
    assert result.shared_minutes[0].hour == 13
    assert result.shared_minutes[0].minute == 30


def test_shared_minutes_are_sorted():
    result = find_overlaps(_expr("* * * * *"), _expr("* * * * *"), ref=REF, window_hours=1)
    assert result.shared_minutes == sorted(result.shared_minutes)


def test_expr_a_and_b_stored():
    a = _expr("0 * * * *")
    b = _expr("30 * * * *")
    result = find_overlaps(a, b, ref=REF, window_hours=2)
    assert result.expr_a == repr(a)
    assert result.expr_b == repr(b)


def test_window_hours_stored():
    result = find_overlaps(_expr("* * * * *"), _expr("* * * * *"), ref=REF, window_hours=3)
    assert result.window_hours == 3


def test_invalid_window_raises():
    with pytest.raises(ValueError):
        find_overlaps(_expr("* * * * *"), _expr("* * * * *"), ref=REF, window_hours=0)


# ---------------------------------------------------------------------------
# OverlapResult.__str__
# ---------------------------------------------------------------------------

def test_str_contains_shared_count():
    result = find_overlaps(_expr("* * * * *"), _expr("* * * * *"), ref=REF, window_hours=1)
    assert "60" in str(result)


def test_str_contains_window():
    result = find_overlaps(_expr("* * * * *"), _expr("* * * * *"), ref=REF, window_hours=2)
    assert "2h" in str(result)


def test_str_no_overlap_omits_first_line():
    result = find_overlaps(
        _expr("0 13 * * *"),
        _expr("0 14 * * *"),
        ref=REF,
        window_hours=1,
    )
    assert "First" not in str(result)
