"""Core cron expression parser for cronlens.

Parses standard 5-field cron expressions (minute, hour, day-of-month,
month, day-of-week) and resolves each field into a sorted list of
valid integer values.
"""

from __future__ import annotations

DAY_NAMES = {
    "sun": 0, "mon": 1, "tue": 2, "wed": 3,
    "thu": 4, "fri": 5, "sat": 6,
}

MONTH_NAMES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

# (min, max) ranges for each cron field
FIELD_RANGES = {
    "minute":      (0, 59),
    "hour":        (0, 23),
    "day_of_month": (1, 31),
    "month":       (1, 12),
    "day_of_week": (0, 6),
}

FIELD_ORDER = ["minute", "hour", "day_of_month", "month", "day_of_week"]

# Well-known shorthand expressions
SHORTHANDS = {
    "@yearly":   "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly":  "0 0 1 * *",
    "@weekly":   "0 0 * * 0",
    "@daily":    "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly":   "0 * * * *",
}


class CronParseError(ValueError):
    """Raised when a cron expression cannot be parsed."""


class CronExpression:
    """Parsed representation of a 5-field cron expression."""

    def __init__(self, expression: str) -> None:
        self.raw = expression.strip()
        self.fields: dict[str, list[int]] = {}
        self._parse()

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:  # pragma: no cover
        return f"CronExpression({self.raw!r})"

    # ------------------------------------------------------------------
    # Internal parsing logic
    # ------------------------------------------------------------------

    def _parse(self) -> None:
        expr = SHORTHANDS.get(self.raw.lower(), self.raw)
        parts = expr.split()
        if len(parts) != 5:
            raise CronParseError(
                f"Expected 5 fields, got {len(parts)}: {self.raw!r}"
            )
        for field_name, part in zip(FIELD_ORDER, parts):
            lo, hi = FIELD_RANGES[field_name]
            self.fields[field_name] = self._resolve_field(part, lo, hi, field_name)

    def _resolve_field(self, token: str, lo: int, hi: int, field_name: str) -> list[int]:
        """Expand a single cron field token into a sorted list of ints."""
        values: set[int] = set()
        for part in token.split(","):
            values.update(self._resolve_part(part, lo, hi, field_name))
        return sorted(values)

    def _resolve_part(self, part: str, lo: int, hi: int, field_name: str) -> list[int]:
        """Handle a single comma-separated segment (range, step, wildcard, literal)."""
        # Step syntax: */n  or  a-b/n
        step = 1
        if "/" in part:
            range_part, step_str = part.split("/", 1)
            step = self._to_int(step_str, field_name)
            if step < 1:
                raise CronParseError(f"Step must be >= 1 in field {field_name!r}")
        else:
            range_part = part

        # Wildcard
        if range_part == "*":
            return list(range(lo, hi + 1, step))

        # Range: a-b
        if "-" in range_part:
            a_str, b_str = range_part.split("-", 1)
            a = self._normalise_value(a_str, field_name)
            b = self._normalise_value(b_str, field_name)
            if a > b:
                raise CronParseError(
                    f"Invalid range {a}-{b} in field {field_name!r}"
                )
            return list(range(a, b + 1, step))

        # Plain value
        value = self._normalise_value(range_part, field_name)
        if step > 1:
            # e.g. "5/15" means 5, 20, 35, 50 ...
            return list(range(value, hi + 1, step))
        return [value]

    def _normalise_value(self, token: str, field_name: str) -> int:
        """Convert a token to an integer, handling named aliases."""
        lower = token.lower()
        if field_name == "day_of_week" and lower in DAY_NAMES:
            return DAY_NAMES[lower]
        if field_name == "month" and lower in MONTH_NAMES:
            return MONTH_NAMES[lower]
        value = self._to_int(token, field_name)
        lo, hi = FIELD_RANGES[field_name]
        if not (lo <= value <= hi):
            raise CronParseError(
                f"Value {value} out of range [{lo}-{hi}] for field {field_name!r}"
            )
        return value

    @staticmethod
    def _to_int(token: str, field_name: str) -> int:
        try:
            return int(token)
        except ValueError:
            raise CronParseError(
                f"Non-numeric token {token!r} in field {field_name!r}"
            )
