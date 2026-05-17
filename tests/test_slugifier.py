"""Tests for cronlens.slugifier."""

import pytest

from cronlens.slugifier import slugify, SlugResult, _field_slug
from cronlens.parser import CronParseError


# ---------------------------------------------------------------------------
# _field_slug unit tests
# ---------------------------------------------------------------------------

def test_field_slug_wildcard():
    assert _field_slug("*", "minute") == "every-minute"


def test_field_slug_step():
    assert _field_slug("*/15", "minute") == "every-15-minutes"


def test_field_slug_range():
    assert _field_slug("9-17", "hour") == "hour-9-to-17"


def test_field_slug_list():
    assert _field_slug("1,3,5", "dow") == "dow-1-3-5"


def test_field_slug_specific():
    assert _field_slug("30", "minute") == "minute-30"


# ---------------------------------------------------------------------------
# slugify integration tests
# ---------------------------------------------------------------------------

def test_slugify_returns_slug_result():
    result = slugify("* * * * *")
    assert isinstance(result, SlugResult)


def test_slugify_stores_expression():
    result = slugify("0 9 * * 1")
    assert result.expression == "0 9 * * 1"


def test_slugify_has_five_tokens():
    result = slugify("*/5 * * * *")
    assert len(result.tokens) == 5


def test_slugify_slug_is_string():
    result = slugify("0 0 * * *")
    assert isinstance(result.slug, str)
    assert len(result.slug) > 0


def test_slugify_slug_no_spaces():
    result = slugify("30 8 * * 1-5")
    assert " " not in result.slug


def test_slugify_slug_safe_chars_only():
    result = slugify("*/10 */2 * * *")
    allowed = set("-_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    assert all(c in allowed for c in result.slug)


def test_slugify_every_minute_contains_every():
    result = slugify("* * * * *")
    assert "every" in result.slug


def test_slugify_invalid_expression_raises():
    with pytest.raises(CronParseError):
        slugify("not a cron")


def test_slugify_str_contains_expression():
    result = slugify("0 12 * * *")
    assert "0 12 * * *" in str(result)


def test_slugify_str_contains_slug():
    result = slugify("0 12 * * *")
    assert result.slug in str(result)


def test_slugify_str_contains_tokens_label():
    result = slugify("0 12 * * *")
    assert "Tokens" in str(result)
