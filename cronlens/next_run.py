"""Compute the next N run times for a given CronExpression."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterator, List

from cronlens.parser import CronExpression

_MAX_ITERATIONS = 366 * 24 * 60  # safety cap: ~1 year of minutes


def _advance_to_next_minute(dt: datetime) -> datetime:
    """Return *dt* rounded up to the next whole minute."""
    return dt.replace(second=0, microsecond=0) + timedelta(minutes=1)


def _matches(expr: CronExpression, dt: datetime) -> bool:
    """Return True if *dt* satisfies all fields of *expr*."""
    return (
        dt.minute in expr.minutes
        and dt.hour in expr.hours
        and dt.day in expr.days
        and dt.month in expr.months
        and dt.weekday() in expr.weekdays
    )


def iter_next_runs(expr: CronExpression, after: datetime | None = None) -> Iterator[datetime]:
    """Yield datetime objects for each future trigger of *expr*.

    Parameters
    ----------
    expr:  A parsed :class:`CronExpression`.
    after: Start searching after this moment (defaults to *now*).
    """
    current = _advance_to_next_minute(after or datetime.now())
    iterations = 0

    while iterations < _MAX_ITERATIONS:
        iterations += 1
        if _matches(expr, current):
            yield current
        current += timedelta(minutes=1)


def next_runs(expr: CronExpression, n: int = 5, after: datetime | None = None) -> List[datetime]:
    """Return the next *n* run times for *expr*."""
    if n < 1:
        raise ValueError("n must be >= 1")
    results: List[datetime] = []
    for dt in iter_next_runs(expr, after=after):
        results.append(dt)
        if len(results) == n:
            break
    return results
