"""Compute previous run times for a cron expression."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterator, List

from cronlens.parser import CronExpression


def _retreat_to_prev_minute(dt: datetime) -> datetime:
    """Floor *dt* to the previous whole minute (subtract one minute, zero seconds)."""
    return (dt - timedelta(minutes=1)).replace(second=0, microsecond=0)


def iter_prev_runs(expr: CronExpression, ref: datetime | None = None) -> Iterator[datetime]:
    """Yield an infinite stream of previous run times, most-recent first.

    Parameters
    ----------
    expr:
        A parsed :class:`~cronlens.parser.CronExpression`.
    ref:
        The reference datetime to look backwards from.  Defaults to *now*.
    """
    if ref is None:
        ref = datetime.now()

    # Start one minute before the reference so we never return *ref* itself.
    current = _retreat_to_prev_minute(ref)

    while True:
        if (
            current.minute in expr.minutes
            and current.hour in expr.hours
            and current.day in expr.days
            and current.month in expr.months
            and current.weekday() in expr.weekdays
        ):
            yield current
        current = _retreat_to_prev_minute(current)


def prev_runs(expr: CronExpression, n: int = 5, ref: datetime | None = None) -> List[datetime]:
    """Return the *n* most-recent previous run times.

    Parameters
    ----------
    expr:
        A parsed :class:`~cronlens.parser.CronExpression`.
    n:
        Number of results to return.  Must be >= 1.
    ref:
        The reference datetime.  Defaults to *now*.

    Raises
    ------
    ValueError
        If *n* is less than 1.
    """
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    results: List[datetime] = []
    for dt in iter_prev_runs(expr, ref=ref):
        results.append(dt)
        if len(results) == n:
            break
    return results
