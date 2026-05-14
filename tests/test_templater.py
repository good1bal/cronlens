"""Tests for cronlens.templater."""

import pytest

from cronlens.templater import (
    Template,
    TemplateError,
    all_templates,
    get,
    known_templates,
    search,
)
from cronlens.parser import CronExpression


# ---------------------------------------------------------------------------
# known_templates
# ---------------------------------------------------------------------------

def test_known_templates_returns_list():
    names = known_templates()
    assert isinstance(names, list)
    assert len(names) > 0


def test_known_templates_sorted():
    names = known_templates()
    assert names == sorted(names)


def test_known_templates_contains_common():
    names = known_templates()
    for expected in ("daily", "hourly", "weekly", "monthly"):
        assert expected in names


# ---------------------------------------------------------------------------
# get
# ---------------------------------------------------------------------------

def test_get_returns_template():
    t = get("daily")
    assert isinstance(t, Template)
    assert t.name == "daily"


def test_get_case_insensitive():
    assert get("Daily").name == "daily"
    assert get("HOURLY").name == "hourly"


def test_get_unknown_raises():
    with pytest.raises(TemplateError, match="Unknown template"):
        get("nonexistent-template")


def test_get_error_lists_available():
    with pytest.raises(TemplateError, match="daily"):
        get("bad")


# ---------------------------------------------------------------------------
# Template.to_cron
# ---------------------------------------------------------------------------

def test_to_cron_returns_cron_expression():
    t = get("every-minute")
    expr = t.to_cron()
    assert isinstance(expr, CronExpression)


def test_to_cron_expression_matches():
    t = get("hourly")
    expr = t.to_cron()
    assert expr.source == "0 * * * *"


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------

def test_search_by_keyword_in_name():
    results = search("daily")
    names = [t.name for t in results]
    assert "daily" in names
    assert "twice-daily" in names


def test_search_by_keyword_in_description():
    results = search("midnight")
    assert len(results) >= 1
    assert all("midnight" in r.description.lower() for r in results)


def test_search_no_match_returns_empty():
    results = search("zzznomatch")
    assert results == []


# ---------------------------------------------------------------------------
# all_templates
# ---------------------------------------------------------------------------

def test_all_templates_count():
    assert len(all_templates()) >= 10


def test_all_templates_str():
    for t in all_templates():
        s = str(t)
        assert t.name in s
        assert t.expression in s
