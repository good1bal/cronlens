"""Tests for cronlens.deduplicator."""

import pytest

from cronlens.deduplicator import deduplicate, DeduplicateResult


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _dedup(*exprs: str) -> DeduplicateResult:
    return deduplicate(list(exprs))


# ---------------------------------------------------------------------------
# basic structure
# ---------------------------------------------------------------------------

def test_returns_deduplicate_result():
    result = _dedup("* * * * *")
    assert isinstance(result, DeduplicateResult)


def test_originals_stored():
    exprs = ["* * * * *", "0 * * * *"]
    result = deduplicate(exprs)
    assert result.originals == exprs


# ---------------------------------------------------------------------------
# unique / duplicate detection
# ---------------------------------------------------------------------------

def test_all_unique_no_duplicates():
    result = _dedup("* * * * *", "0 * * * *", "0 0 * * *")
    assert result.unique_count == 3
    assert result.removed_count == 0
    assert result.duplicates == {}


def test_exact_duplicate_detected():
    result = _dedup("* * * * *", "* * * * *")
    assert result.unique_count == 1
    assert result.removed_count == 1


def test_duplicate_grouped_under_first_seen():
    result = _dedup("0 12 * * *", "0 12 * * *", "0 12 * * *")
    assert result.removed_count == 2
    canonical_key = list(result.duplicates.keys())[0]
    assert canonical_key == "0 12 * * *"


def test_multiple_duplicate_groups():
    result = _dedup(
        "* * * * *", "* * * * *",
        "0 0 * * *", "0 0 * * *",
    )
    assert result.unique_count == 2
    assert len(result.duplicates) == 2


def test_unique_list_preserves_first_occurrence():
    result = _dedup("* * * * *", "0 * * * *", "* * * * *")
    assert "* * * * *" in result.unique
    assert "0 * * * *" in result.unique
    assert result.unique_count == 2


# ---------------------------------------------------------------------------
# invalid expressions
# ---------------------------------------------------------------------------

def test_invalid_expression_goes_to_invalid_list():
    result = _dedup("not_a_cron", "* * * * *")
    assert "not_a_cron" in result.invalid
    assert result.unique_count == 1


def test_invalid_does_not_count_as_unique_or_duplicate():
    result = _dedup("bad expr", "also bad")
    assert result.unique_count == 0
    assert result.removed_count == 0
    assert len(result.invalid) == 2


# ---------------------------------------------------------------------------
# counts
# ---------------------------------------------------------------------------

def test_removed_count_zero_when_no_duplicates():
    result = _dedup("* * * * *")
    assert result.removed_count == 0


def test_removed_count_correct():
    result = _dedup("* * * * *", "* * * * *", "* * * * *")
    assert result.removed_count == 2


# ---------------------------------------------------------------------------
# __str__
# ---------------------------------------------------------------------------

def test_str_contains_unique_count():
    result = _dedup("* * * * *", "0 * * * *")
    assert "Unique" in str(result)


def test_str_contains_duplicates_section_when_present():
    result = _dedup("* * * * *", "* * * * *")
    assert "Duplicate groups" in str(result)


def test_str_no_duplicate_section_when_all_unique():
    result = _dedup("* * * * *", "0 * * * *")
    assert "Duplicate groups" not in str(result)


def test_str_contains_invalid_section_when_present():
    result = _dedup("bad", "* * * * *")
    assert "Invalid expressions" in str(result)
