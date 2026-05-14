"""Maps well-known cron aliases (@yearly, @daily, etc.) to standard expressions."""

from __future__ import annotations

from typing import Optional

# Canonical alias -> raw cron expression mapping
_ALIASES: dict[str, str] = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
    "@every_minute": "* * * * *",
    "@reboot": None,  # Not representable as a standard 5-field expression
}


class AliasError(Exception):
    """Raised when an alias cannot be resolved to a cron expression."""


def is_alias(value: str) -> bool:
    """Return True if *value* looks like a cron alias (starts with '@')."""
    return value.startswith("@")


def resolve(alias: str) -> str:
    """Resolve *alias* to its equivalent 5-field cron expression.

    Raises
    ------
    AliasError
        If the alias is unknown or cannot be represented as a standard
        5-field expression (e.g. ``@reboot``).
    """
    key = alias.lower()
    if key not in _ALIASES:
        raise AliasError(f"Unknown alias: {alias!r}")
    expression = _ALIASES[key]
    if expression is None:
        raise AliasError(
            f"Alias {alias!r} has no equivalent 5-field cron expression"
        )
    return expression


def known_aliases() -> list[str]:
    """Return all recognised alias names sorted alphabetically."""
    return sorted(_ALIASES.keys())


def alias_table() -> list[tuple[str, Optional[str]]]:
    """Return a list of (alias, expression) pairs for display purposes.

    Entries whose expression is ``None`` are included with ``None`` as the
    second element so callers can render them appropriately.
    """
    return [(k, v) for k, v in sorted(_ALIASES.items())]
