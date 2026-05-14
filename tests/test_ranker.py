"""Tests for cronlens.ranker."""

import pytest

from cronlens.ranker import rank, RankResult, RankEntry, SORTABLE_CRITERIA


SIMPLE = "* * * * *"
HOURLY = "0 * * * *"
DAILY = "0 9 * * *"
COMPLEX = "5,15,30 8-18/2 1,15 3,6,9 1-5"


# ---------------------------------------------------------------------------
# Basic return types
# ---------------------------------------------------------------------------

def test_rank_returns_rank_result():
    result = rank([SIMPLE, HOURLY, DAILY])
    assert isinstance(result, RankResult)


def test_rank_entry_count_matches_input():
    exprs = [SIMPLE, HOURLY, DAILY, COMPLEX]
    result = rank(exprs)
    assert len(result.entries) == len(exprs)


def test_rank_entries_are_rank_entry_instances():
    result = rank([SIMPLE, DAILY])
    for entry in result.entries:
        assert isinstance(entry, RankEntry)


# ---------------------------------------------------------------------------
# Rank numbering
# ---------------------------------------------------------------------------

def test_rank_numbers_start_at_one():
    result = rank([SIMPLE, HOURLY, DAILY])
    assert result.entries[0].rank == 1


def test_rank_numbers_are_sequential():
    result = rank([SIMPLE, HOURLY, DAILY, COMPLEX])
    ranks = [e.rank for e in result.entries]
    assert ranks == list(range(1, len(ranks) + 1))


# ---------------------------------------------------------------------------
# Criterion and ordering
# ---------------------------------------------------------------------------

def test_default_criterion_is_score():
    result = rank([SIMPLE, DAILY])
    assert result.criterion == "score"


def test_default_ascending_is_true():
    result = rank([SIMPLE, DAILY])
    assert result.ascending is True


def test_sort_ascending_by_complexity():
    result = rank([COMPLEX, SIMPLE, DAILY], criterion="complexity", ascending=True)
    complexities = [e.result.complexity for e in result.entries]
    assert complexities == sorted(complexities)


def test_sort_descending_by_complexity():
    result = rank([SIMPLE, COMPLEX, DAILY], criterion="complexity", ascending=False)
    complexities = [e.result.complexity for e in result.entries]
    assert complexities == sorted(complexities, reverse=True)


def test_sort_by_predictability():
    result = rank([COMPLEX, SIMPLE, HOURLY], criterion="predictability", ascending=True)
    vals = [e.result.predictability for e in result.entries]
    assert vals == sorted(vals)


def test_sort_by_score():
    result = rank([COMPLEX, DAILY, SIMPLE], criterion="score", ascending=True)
    vals = [e.result.score for e in result.entries]
    assert vals == sorted(vals)


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_unknown_criterion_raises():
    with pytest.raises(ValueError, match="Unknown criterion"):
        rank([SIMPLE], criterion="foobar")


def test_invalid_expression_raises():
    from cronlens.parser import CronParseError
    with pytest.raises(CronParseError):
        rank(["not a cron"])


# ---------------------------------------------------------------------------
# __str__
# ---------------------------------------------------------------------------

def test_rank_result_str_contains_criterion():
    result = rank([SIMPLE, DAILY], criterion="complexity")
    assert "complexity" in str(result)


def test_rank_entry_str_contains_expression():
    result = rank([DAILY])
    assert DAILY in str(result.entries[0])


def test_rank_result_str_contains_all_expressions():
    exprs = [SIMPLE, HOURLY, DAILY]
    result = rank(exprs)
    output = str(result)
    for expr in exprs:
        assert expr in output
