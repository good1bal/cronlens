"""Tests for cronlens.validator."""

import pytest
from cronlens.validator import validate, FieldError, ValidationResult, FIELD_NAMES


def test_valid_every_minute():
    result = validate("* * * * *")
    assert result.valid
    assert result.errors == []


def test_valid_specific_values():
    result = validate("30 6 1 1 0")
    assert result.valid


def test_valid_ranges():
    result = validate("0-30 8-18 * * 1-5")
    assert result.valid


def test_valid_step():
    result = validate("*/15 * * * *")
    assert result.valid


def test_valid_comma_list():
    result = validate("0,15,30,45 * * * *")
    assert result.valid


def test_wrong_field_count_too_few():
    result = validate("* * * *")
    assert not result.valid
    assert any("5 fields" in e.message for e in result.errors)


def test_wrong_field_count_too_many():
    result = validate("* * * * * *")
    assert not result.valid


def test_minute_out_of_range():
    result = validate("60 * * * *")
    assert not result.valid
    assert result.errors[0].field_name == "minute"


def test_hour_out_of_range():
    result = validate("0 24 * * *")
    assert not result.valid
    assert result.errors[0].field_name == "hour"


def test_day_out_of_range():
    result = validate("0 0 0 * *")
    assert not result.valid
    assert result.errors[0].field_name == "day"


def test_month_out_of_range():
    result = validate("0 0 1 13 *")
    assert not result.valid
    assert result.errors[0].field_name == "month"


def test_weekday_boundary_7_is_valid():
    result = validate("0 0 * * 7")
    assert result.valid


def test_invalid_step_zero():
    result = validate("*/0 * * * *")
    assert not result.valid
    assert "step" in result.errors[0].message


def test_invalid_range_reversed():
    result = validate("30-10 * * * *")
    assert not result.valid
    assert "exceeds" in result.errors[0].message


def test_non_numeric_token():
    result = validate("abc * * * *")
    assert not result.valid


def test_multiple_errors_reported():
    result = validate("99 99 * * *")
    assert not result.valid
    assert len(result.errors) == 2


def test_error_summary_no_errors():
    result = validate("* * * * *")
    assert result.error_summary() == "No errors."


def test_error_summary_contains_field_name():
    result = validate("99 * * * *")
    summary = result.error_summary()
    assert "minute" in summary


def test_bool_true_when_valid():
    assert bool(validate("* * * * *")) is True


def test_bool_false_when_invalid():
    assert bool(validate("99 * * * *")) is False
