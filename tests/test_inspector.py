"""Tests for cronlens.inspector."""

from __future__ import annotations

import pytest

from cronlens.inspector import FieldInspection, InspectResult, inspect, _resolve_values
from cronlens.parser import CronParseError


# ---------------------------------------------------------------------------
# _resolve_values helpers
# ---------------------------------------------------------------------------

def test_wildcard_resolves_to_full_range():
    assert _resolve_values("*", range(0, 5)) == [0, 1, 2, 3, 4]


def test_single_value_resolves_correctly():
    assert _resolve_values("3", range(0, 60)) == [3]


def test_range_token_resolves_correctly():
    assert _resolve_values("1-3", range(0, 60)) == [1, 2, 3]


def test_step_token_resolves_correctly():
    assert _resolve_values("*/15", range(0, 60)) == [0, 15, 30, 45]


def test_comma_list_resolves_correctly():
    assert _resolve_values("1,3,5", range(0, 60)) == [1, 3, 5]


def test_step_with_range_base():
    assert _resolve_values("0-6/2", range(0, 60)) == [0, 2, 4, 6]


# ---------------------------------------------------------------------------
# inspect() return type
# ---------------------------------------------------------------------------

def _expr(s: str) -> InspectResult:
    return inspect(s)


def test_inspect_returns_inspect_result():
    assert isinstance(_expr("* * * * *"), InspectResult)


def test_inspect_has_five_fields():
    result = _expr("* * * * *")
    assert len(result.fields) == 5


def test_fields_are_field_inspection_instances():
    result = _expr("* * * * *")
    for f in result.fields:
        assert isinstance(f, FieldInspection)


def test_field_names_are_correct():
    result = _expr("* * * * *")
    names = [f.name for f in result.fields]
    assert names == ["minute", "hour", "day", "month", "weekday"]


def test_expression_stored():
    expr = "0 9 * * 1"
    result = _expr(expr)
    assert result.expression == expr


def test_every_minute_minute_field_has_60_values():
    result = _expr("* * * * *")
    minute_field = result.fields[0]
    assert len(minute_field.values) == 60


def test_specific_minute_resolves_to_single_value():
    result = _expr("30 * * * *")
    assert result.fields[0].values == [30]


def test_specific_hour_resolves_correctly():
    result = _expr("0 9 * * *")
    assert result.fields[1].values == [9]


def test_weekday_field_resolves_correctly():
    result = _expr("0 9 * * 1-5")
    assert result.fields[4].values == [1, 2, 3, 4, 5]


def test_month_step_resolves_correctly():
    result = _expr("0 0 1 */3 *")
    assert result.fields[3].values == [1, 4, 7, 10]


def test_invalid_expression_raises():
    with pytest.raises(CronParseError):
        inspect("not a cron")


# ---------------------------------------------------------------------------
# __str__ representations
# ---------------------------------------------------------------------------

def test_field_inspection_str_contains_name():
    result = _expr("* * * * *")
    assert "minute" in str(result.fields[0])


def test_inspect_result_str_contains_expression():
    result = _expr("0 12 * * *")
    assert "0 12 * * *" in str(result)


def test_inspect_result_str_has_header_row():
    result = _expr("* * * * *")
    text = str(result)
    assert "Field" in text and "Token" in text
