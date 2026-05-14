"""Classify a cron expression into a human-readable schedule category."""

from __future__ import annotations
from dataclasses import dataclass
from typing import List

from cronlens.parser import CronExpression

# Category constants
EVERY_MINUTE = "every-minute"
HOURLY = "hourly"
DAILY = "daily"
WEEKLY = "weekly"
MONTHLY = "monthly"
YEARLY = "yearly"
CUSTOM = "custom"

_ORDERED_CATEGORIES = [EVERY_MINUTE, HOURLY, DAILY, WEEKLY, MONTHLY, YEARLY, CUSTOM]


@dataclass
class ClassifyResult:
    expression: str
    category: str
    description: str

    def __str__(self) -> str:
        return f"{self.expression!r} → [{self.category}] {self.description}"


def _is_wildcard(field_values: List[int], full_range: range) -> bool:
    """Return True when field_values covers every value in full_range."""
    return set(field_values) == set(full_range)


def classify(expr: CronExpression) -> ClassifyResult:
    """Classify *expr* and return a :class:`ClassifyResult`."""
    minute_wild = _is_wildcard(expr.minutes, range(0, 60))
    hour_wild = _is_wildcard(expr.hours, range(0, 24))
    dom_wild = _is_wildcard(expr.days_of_month, range(1, 32))
    month_wild = _is_wildcard(expr.months, range(1, 13))
    dow_wild = _is_wildcard(expr.days_of_week, range(0, 7))

    if minute_wild and hour_wild and dom_wild and month_wild and dow_wild:
        return ClassifyResult(str(expr), EVERY_MINUTE, "Runs every minute")

    if not minute_wild and hour_wild and dom_wild and month_wild and dow_wild:
        return ClassifyResult(str(expr), HOURLY, "Runs once per hour")

    if not minute_wild and not hour_wild and dom_wild and month_wild and dow_wild:
        return ClassifyResult(str(expr), DAILY, "Runs once per day")

    if not minute_wild and not hour_wild and dom_wild and month_wild and not dow_wild:
        return ClassifyResult(str(expr), WEEKLY, "Runs on specific weekdays")

    if not minute_wild and not hour_wild and not dom_wild and month_wild and dow_wild:
        return ClassifyResult(str(expr), MONTHLY, "Runs on specific days of the month")

    if not minute_wild and not hour_wild and not dom_wild and not month_wild and dow_wild:
        return ClassifyResult(str(expr), YEARLY, "Runs once per year")

    return ClassifyResult(str(expr), CUSTOM, "Custom schedule")
