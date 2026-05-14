"""Tests for cronlens.annotator."""

import pytest

from cronlens.annotator import annotate, AnnotationResult, AnnotatedField
from cronlens.parser import CronParseError


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _ann(expr: str) -> AnnotationResult:
    return annotate(expr)


# ---------------------------------------------------------------------------
# structure tests
# ---------------------------------------------------------------------------

def test_annotate_returns_annotation_result():
    result = _ann("* * * * *")
    assert isinstance(result, AnnotationResult)


def test_annotate_has_five_fields():
    result = _ann("* * * * *")
    assert len(result.fields) == 5


def test_fields_are_annotated_field_instances():
    result = _ann("0 9 * * 1")
    for field in result.fields:
        assert isinstance(field, AnnotatedField)


def test_field_names_are_correct():
    result = _ann("* * * * *")
    names = [f.name for f in result.fields]
    assert names == ["minute", "hour", "day", "month", "weekday"]


def test_tokens_match_expression_parts():
    expr = "5 10 * * 1-5"
    result = _ann(expr)
    tokens = [f.token for f in result.fields]
    assert tokens == ["5", "10", "*", "*", "1-5"]


def test_annotation_is_non_empty_string():
    result = _ann("0 0 * * *")
    for field in result.fields:
        assert isinstance(field.annotation, str)
        assert len(field.annotation) > 0


# ---------------------------------------------------------------------------
# __str__ tests
# ---------------------------------------------------------------------------

def test_str_contains_expression_as_comment():
    expr = "*/5 * * * *"
    result = _ann(expr)
    assert f"# {expr}" in str(result)


def test_str_contains_all_tokens():
    expr = "0 9 * * 1"
    result = _ann(expr)
    text = str(result)
    for token in ["0", "9", "*", "*", "1"]:
        assert token in text


def test_annotated_field_str_contains_name_and_token():
    field = next(f for f in _ann("30 6 * * *").fields if f.name == "minute")
    text = str(field)
    assert "minute" in text
    assert "30" in text


def test_str_has_five_field_lines():
    result = _ann("* * * * *")
    # first line is the header comment
    lines = str(result).splitlines()
    assert len(lines) == 6


# ---------------------------------------------------------------------------
# error handling
# ---------------------------------------------------------------------------

def test_invalid_expression_raises():
    with pytest.raises(CronParseError):
        annotate("not a cron")


def test_too_few_fields_raises():
    with pytest.raises(CronParseError):
        annotate("* * *")
