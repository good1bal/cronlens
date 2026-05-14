"""Tests for cronlens.aliaser."""

import pytest

from cronlens.aliaser import (
    AliasError,
    alias_table,
    is_alias,
    known_aliases,
    resolve,
)


# ---------------------------------------------------------------------------
# is_alias
# ---------------------------------------------------------------------------

def test_is_alias_true_for_at_prefix():
    assert is_alias("@daily") is True


def test_is_alias_false_for_plain_expression():
    assert is_alias("0 0 * * *") is False


def test_is_alias_false_for_empty_string():
    assert is_alias("") is False


# ---------------------------------------------------------------------------
# resolve – happy paths
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("alias,expected", [
    ("@yearly",      "0 0 1 1 *"),
    ("@annually",    "0 0 1 1 *"),
    ("@monthly",     "0 0 1 * *"),
    ("@weekly",      "0 0 * * 0"),
    ("@daily",       "0 0 * * *"),
    ("@midnight",    "0 0 * * *"),
    ("@hourly",      "0 * * * *"),
    ("@every_minute", "* * * * *"),
])
def test_resolve_known_aliases(alias, expected):
    assert resolve(alias) == expected


def test_resolve_is_case_insensitive():
    assert resolve("@DAILY") == "0 0 * * *"
    assert resolve("@Hourly") == "0 * * * *"


# ---------------------------------------------------------------------------
# resolve – error paths
# ---------------------------------------------------------------------------

def test_resolve_unknown_alias_raises():
    with pytest.raises(AliasError, match="Unknown alias"):
        resolve("@unknown")


def test_resolve_reboot_raises_alias_error():
    with pytest.raises(AliasError, match="no equivalent"):
        resolve("@reboot")


# ---------------------------------------------------------------------------
# known_aliases
# ---------------------------------------------------------------------------

def test_known_aliases_returns_list():
    aliases = known_aliases()
    assert isinstance(aliases, list)
    assert len(aliases) > 0


def test_known_aliases_sorted():
    aliases = known_aliases()
    assert aliases == sorted(aliases)


def test_known_aliases_includes_common():
    aliases = known_aliases()
    for name in ("@daily", "@hourly", "@weekly", "@monthly", "@yearly"):
        assert name in aliases


# ---------------------------------------------------------------------------
# alias_table
# ---------------------------------------------------------------------------

def test_alias_table_returns_pairs():
    table = alias_table()
    assert all(isinstance(row, tuple) and len(row) == 2 for row in table)


def test_alias_table_includes_reboot_as_none():
    table = dict(alias_table())
    assert "@reboot" in table
    assert table["@reboot"] is None


def test_alias_table_length_matches_known_aliases():
    assert len(alias_table()) == len(known_aliases())
