"""Field-level inspector: shows the resolved set of values for each cron field."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from cronlens.parser import CronExpression, CronParseError

_FIELD_NAMES = ("minute", "hour", "day", "month", "weekday")
_FIELD_RANGES = {
    "minute": range(0, 60),
    "hour": range(0, 24),
    "day": range(1, 32),
    "month": range(1, 13),
    "weekday": range(0, 7),
}


@dataclass
class FieldInspection:
    name: str
    raw: str
    values: List[int]

    def __str__(self) -> str:
        vals = ", ".join(str(v) for v in self.values)
        return f"{self.name:<10} {self.raw:<20} [{vals}]"


@dataclass
class InspectResult:
    expression: str
    fields: List[FieldInspection] = field(default_factory=list)

    def __str__(self) -> str:
        header = f"Inspection: {self.expression}\n"
        header += f"{'Field':<10} {'Token':<20} Resolved values\n"
        header += "-" * 60 + "\n"
        rows = "\n".join(str(f) for f in self.fields)
        return header + rows


def _resolve_values(raw: str, full_range: range) -> List[int]:
    """Return the sorted list of integers that a single cron token expands to."""
    if raw == "*":
        return list(full_range)

    values: set[int] = set()
    for part in raw.split(","):
        if "/" in part:
            base, step_str = part.split("/", 1)
            step = int(step_str)
            if base == "*":
                start, stop = full_range.start, full_range.stop
            elif "-" in base:
                a, b = base.split("-", 1)
                start, stop = int(a), int(b) + 1
            else:
                start, stop = int(base), full_range.stop
            values.update(range(start, stop, step))
        elif "-" in part:
            a, b = part.split("-", 1)
            values.update(range(int(a), int(b) + 1))
        else:
            values.add(int(part))
    return sorted(v for v in values if v in full_range)


def inspect(expression: str) -> InspectResult:
    """Parse *expression* and return an InspectResult with resolved field values."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        raise CronParseError(str(exc)) from exc

    raw_fields = (
        expr.minute,
        expr.hour,
        expr.day,
        expr.month,
        expr.weekday,
    )

    inspections = [
        FieldInspection(
            name=name,
            raw=raw,
            values=_resolve_values(raw, _FIELD_RANGES[name]),
        )
        for name, raw in zip(_FIELD_NAMES, raw_fields)
    ]

    return InspectResult(expression=expression, fields=inspections)
