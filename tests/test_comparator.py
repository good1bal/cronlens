"""Tests for cronlens.comparator."""

from datetime import datetime

import pytest

from cronlens.parser import CronExpression
from cronlens.comparator import compare, CompareResult


REF = datetime(2024, 1, 1, 0, 0, 0)


def _expr(s: str) -> CronExpression:
    return CronExpression(s)


# ---------------------------------------------------------------------------
# Basic structure
# ---------------------------------------------------------------------------

def test_compare_returns_compare_result():
    result = compare(_expr("* * * * *"), _expr("* * * * *"), n=5, ref=REF)
    assert isinstance(result, CompareResult)


def test_identical_expressions_all_shared():
    result = compare(_expr("* * * * *"), _expr("* * * * *"), n=10, ref=REF)
    assert len(result.shared) == 10
    assert len(result.only_a) == 0
    assert len(result.only_b) == 0


def test_disjoint_expressions_no_shared():
    # minute 0 vs minute 1 — within a 60-run window these never overlap
    result = compare(_expr("0 * * * *"), _expr("1 * * * *"), n=5, ref=REF)
    assert len(result.shared) == 0
    assert len(result.only_a) > 0
    assert len(result.only_b) > 0


def test_overlap_count_matches_shared_length():
    result = compare(_expr("* * * * *"), _expr("0 * * * *"), n=60, ref=REF)
    assert result.overlap_count == len(result.shared)


# ---------------------------------------------------------------------------
# Overlap percentages
# ---------------------------------------------------------------------------

def test_overlap_pct_identical_is_100():
    result = compare(_expr("* * * * *"), _expr("* * * * *"), n=10, ref=REF)
    assert result.overlap_pct_a == pytest.approx(100.0)
    assert result.overlap_pct_b == pytest.approx(100.0)


def test_overlap_pct_disjoint_is_zero():
    result = compare(_expr("0 * * * *"), _expr("1 * * * *"), n=5, ref=REF)
    assert result.overlap_pct_a == pytest.approx(0.0)
    assert result.overlap_pct_b == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Summary string
# ---------------------------------------------------------------------------

def test_summary_contains_expressions():
    a = _expr("0 * * * *")
    b = _expr("30 * * * *")
    result = compare(a, b, n=5, ref=REF)
    s = result.summary()
    assert "0 * * * *" in s
    assert "30 * * * *" in s


def test_summary_contains_shared_label():
    result = compare(_expr("* * * * *"), _expr("* * * * *"), n=5, ref=REF)
    assert "Shared" in result.summary()


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_n_less_than_one_raises():
    with pytest.raises(ValueError):
        compare(_expr("* * * * *"), _expr("* * * * *"), n=0, ref=REF)


def test_total_a_and_b_correct():
    result = compare(_expr("* * * * *"), _expr("0 * * * *"), n=60, ref=REF)
    assert result.total_a == len(result.shared) + len(result.only_a)
    assert result.total_b == len(result.shared) + len(result.only_b)
