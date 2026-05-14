"""Tests for cronlens.scorer."""

import pytest

from cronlens.parser import CronExpression
from cronlens.scorer import ScoreResult, score


def _expr(s: str) -> CronExpression:
    return CronExpression(s)


# ---------------------------------------------------------------------------
# ScoreResult
# ---------------------------------------------------------------------------

class TestScoreResult:
    def test_str_contains_expression(self):
        r = ScoreResult(expression="* * * * *", complexity=0, predictability=100, notes=[])
        assert "* * * * *" in str(r)

    def test_str_contains_complexity(self):
        r = ScoreResult(expression="* * * * *", complexity=42, predictability=58, notes=[])
        assert "42" in str(r)

    def test_str_contains_predictability(self):
        r = ScoreResult(expression="* * * * *", complexity=0, predictability=100, notes=[])
        assert "100" in str(r)

    def test_str_contains_notes_when_present(self):
        r = ScoreResult(expression="x", complexity=5, predictability=95, notes=["hello"])
        assert "hello" in str(r)

    def test_str_no_notes_section_when_empty(self):
        r = ScoreResult(expression="x", complexity=5, predictability=95, notes=[])
        assert "Notes" not in str(r)


# ---------------------------------------------------------------------------
# score()
# ---------------------------------------------------------------------------

def test_score_returns_score_result():
    result = score(_expr("* * * * *"))
    assert isinstance(result, ScoreResult)


def test_every_minute_low_complexity():
    result = score(_expr("* * * * *"))
    assert result.complexity <= 10


def test_every_minute_high_predictability():
    result = score(_expr("* * * * *"))
    assert result.predictability >= 90


def test_specific_values_higher_complexity_than_wildcard():
    simple = score(_expr("* * * * *"))
    specific = score(_expr("30 6 * * *"))
    assert specific.complexity > simple.complexity


def test_complexity_plus_predictability_equals_100():
    for expr_str in ["* * * * *", "0 9 * * 1", "*/15 * * * *", "0 0 1 1 *"]:
        result = score(_expr(expr_str))
        assert result.complexity + result.predictability == 100


def test_complexity_in_range():
    result = score(_expr("5,10,15 1-5 */2 6,12 1"))
    assert 0 <= result.complexity <= 100


def test_comma_list_noted():
    result = score(_expr("0 6,12,18 * * *"))
    assert any("hour" in n for n in result.notes)


def test_day_and_weekday_both_set_noted():
    result = score(_expr("0 9 15 * 1"))
    assert any("day" in n.lower() and "weekday" in n.lower() for n in result.notes)


def test_very_simple_note_present():
    result = score(_expr("* * * * *"))
    assert any("simple" in n.lower() for n in result.notes)


def test_complex_expression_higher_than_simple():
    simple = score(_expr("0 0 * * *"))
    complex_ = score(_expr("5,10,20,30,40,50 */2 1,15 1,6,12 1,3,5"))
    assert complex_.complexity > simple.complexity


def test_step_expression_intermediate_complexity():
    wildcard = score(_expr("* * * * *"))
    step = score(_expr("*/15 * * * *"))
    specific = score(_expr("0,15,30,45 * * * *"))
    assert wildcard.complexity <= step.complexity <= specific.complexity
