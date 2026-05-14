"""Named cron templates: predefined expressions with descriptions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from cronlens.parser import CronExpression


@dataclass
class Template:
    name: str
    expression: str
    description: str

    def to_cron(self) -> CronExpression:
        return CronExpression(self.expression)

    def __str__(self) -> str:
        return f"{self.name}: {self.expression!r} — {self.description}"


_TEMPLATES: List[Template] = [
    Template("every-minute",    "* * * * *",     "Runs every minute"),
    Template("hourly",          "0 * * * *",     "Runs at the start of every hour"),
    Template("daily",           "0 0 * * *",     "Runs once a day at midnight"),
    Template("weekly",          "0 0 * * 0",     "Runs once a week on Sunday at midnight"),
    Template("monthly",         "0 0 1 * *",     "Runs on the first day of every month"),
    Template("yearly",          "0 0 1 1 *",     "Runs once a year on January 1st"),
    Template("weekdays",        "0 9 * * 1-5",   "Runs at 09:00 on weekdays (Mon–Fri)"),
    Template("twice-daily",     "0 0,12 * * *",  "Runs at midnight and noon"),
    Template("every-5-minutes", "*/5 * * * *",   "Runs every 5 minutes"),
    Template("every-15-minutes","*/15 * * * *",  "Runs every 15 minutes"),
    Template("every-30-minutes","*/30 * * * *",  "Runs every 30 minutes"),
    Template("business-hours",  "0 9-17 * * 1-5","Runs hourly during business hours on weekdays"),
]

_INDEX: Dict[str, Template] = {t.name: t for t in _TEMPLATES}


class TemplateError(Exception):
    """Raised when a requested template does not exist."""


def known_templates() -> List[str]:
    """Return sorted list of all template names."""
    return sorted(_INDEX.keys())


def get(name: str) -> Template:
    """Return the Template for *name* (case-insensitive).

    Raises TemplateError if the name is unknown.
    """
    key = name.strip().lower()
    if key not in _INDEX:
        raise TemplateError(
            f"Unknown template {name!r}. "
            f"Available: {', '.join(known_templates())}"
        )
    return _INDEX[key]


def search(keyword: str) -> List[Template]:
    """Return templates whose name or description contain *keyword* (case-insensitive)."""
    kw = keyword.lower()
    return [
        t for t in _TEMPLATES
        if kw in t.name or kw in t.description.lower()
    ]


def all_templates() -> List[Template]:
    """Return all registered templates in definition order."""
    return list(_TEMPLATES)
