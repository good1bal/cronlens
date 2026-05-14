"""Tests for cronlens.linter."""

import pytest
from cronlens.linter import lint, LintResult, LintWarning


def test_valid_no_warnings():
    result = lint("0 9 * * 1-5")
    assert result.ok
    assert not result.has_warnings()


def test_invalid_expression_not_ok():
    result = lint("99 * * * *")
    assert not result.ok


def test_invalid_no_semantic_warnings():
    # semantic checks should not run on invalid expressions
    result = lint("99 * 1 * 1")
    assert not result.ok
    assert not result.has_warnings()


def test_every_minute_warns():
    result = lint("* * * * *")
    assert result.ok
    assert result.has_warnings()
    messages = [str(w) for w in result.warnings]
    assert any("every minute" in m for m in messages)


def test_day_and_weekday_both_set_warns():
    result = lint("0 0 1 * 1")
    assert result.ok
    assert result.has_warnings()
    messages = [str(w) for w in result.warnings]
    assert any("day-of-month" in m for m in messages)


def test_feb_day_30_warns():
    result = lint("0 0 30 2 *")
    assert result.ok
    assert result.has_warnings()
    messages = [str(w) for w in result.warnings]
    assert any("February" in m for m in messages)


def test_feb_day_28_no_warn():
    result = lint("0 0 28 2 *")
    assert result.ok
    # day 28 in Feb is fine
    feb_warns = [w for w in result.warnings if "February" in str(w)]
    assert feb_warns == []


def test_report_contains_expression():
    result = lint("0 9 * * 1-5")
    assert "0 9 * * 1-5" in result.report()


def test_report_shows_valid_status():
    result = lint("0 9 * * 1-5")
    assert "valid" in result.report()


def test_report_shows_invalid_status():
    result = lint("99 * * * *")
    assert "INVALID" in result.report()


def test_report_shows_warnings():
    result = lint("* * * * *")
    assert "WARN" in result.report()


def test_lint_result_ok_property():
    assert lint("* * * * *").ok is True
    assert lint("bad expression here").ok is False
