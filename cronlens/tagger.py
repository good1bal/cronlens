"""Tag cron expressions with human-friendly category labels."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from cronlens.parser import CronExpression

# (tag, description)
_TAGS: list[tuple[str, str]] = [
    ("every-minute", "Runs every single minute (high frequency)"),
    ("hourly", "Runs once per hour"),
    ("daily", "Runs once per day"),
    ("weekly", "Runs once per week"),
    ("monthly", "Runs once per month"),
    ("weekday-only", "Restricted to specific weekday(s)"),
    ("month-restricted", "Restricted to specific month(s)"),
    ("multiple-times-per-hour", "Runs more than once per hour"),
    ("multiple-times-per-day", "Runs more than once per day"),
]


@dataclass
class TagResult:
    expression: str
    tags: List[str] = field(default_factory=list)

    def __str__(self) -> str:  # pragma: no cover
        if not self.tags:
            return f"{self.expression}: (no tags)"
        return f"{self.expression}: {', '.join(self.tags)}"


def tag(expr: CronExpression) -> TagResult:
    """Return a TagResult with all applicable tags for *expr*."""
    tags: list[str] = []

    minute = expr.minute
    hour = expr.hour
    dom = expr.day_of_month
    month = expr.month
    dow = expr.day_of_week

    is_wildcard = lambda f: f == ["*"]  # noqa: E731

    # every-minute
    if is_wildcard(minute) and is_wildcard(hour):
        tags.append("every-minute")

    # multiple-times-per-hour (step on minute, e.g. */5)
    if not is_wildcard(minute) and not tags:
        if any("/" in str(m) for m in minute):
            tags.append("multiple-times-per-hour")

    # multiple-times-per-day
    if is_wildcard(minute) and not is_wildcard(hour) and len(hour) > 1:
        tags.append("multiple-times-per-day")

    # hourly: minute is specific, hour is wildcard
    if not is_wildcard(minute) and is_wildcard(hour) and is_wildcard(dom) and is_wildcard(dow):
        if "every-minute" not in tags and "multiple-times-per-hour" not in tags:
            tags.append("hourly")

    # daily
    if (
        not is_wildcard(minute)
        and not is_wildcard(hour)
        and len(hour) == 1
        and is_wildcard(dom)
        and is_wildcard(dow)
        and "multiple-times-per-day" not in tags
    ):
        tags.append("daily")

    # weekly
    if not is_wildcard(dow) and is_wildcard(dom):
        tags.append("weekly")
        tags.append("weekday-only")

    # monthly
    if not is_wildcard(dom) and is_wildcard(dow) and "daily" not in tags:
        tags.append("monthly")

    # weekday-only (without implying weekly)
    if not is_wildcard(dow) and "weekday-only" not in tags:
        tags.append("weekday-only")

    # month-restricted
    if not is_wildcard(month):
        tags.append("month-restricted")

    return TagResult(expression=repr(expr), tags=tags)
