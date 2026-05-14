"""Aggregate statistics and summary metrics for a cron expression."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

from cronlens.next_run import next_runs
from cronlens.parser import CronExpression


@dataclass
class RunStats:
    """Statistical summary of upcoming cron runs."""

    expression: str
    sample_size: int
    min_gap_seconds: float
    max_gap_seconds: float
    avg_gap_seconds: float
    runs_per_hour: float
    runs_per_day: float
    next_run: datetime
    intervals: List[float] = field(repr=False)

    @property
    def min_gap(self) -> timedelta:
        return timedelta(seconds=self.min_gap_seconds)

    @property
    def max_gap(self) -> timedelta:
        return timedelta(seconds=self.max_gap_seconds)

    @property
    def avg_gap(self) -> timedelta:
        return timedelta(seconds=self.avg_gap_seconds)

    def __str__(self) -> str:
        lines = [
            f"Expression : {self.expression}",
            f"Sample size: {self.sample_size} runs",
            f"Next run   : {self.next_run.strftime('%Y-%m-%d %H:%M')}",
            f"Min gap    : {self.min_gap}",
            f"Max gap    : {self.max_gap}",
            f"Avg gap    : {self.avg_gap}",
            f"Runs/hour  : {self.runs_per_hour:.2f}",
            f"Runs/day   : {self.runs_per_day:.2f}",
        ]
        return "\n".join(lines)


def summarize(
    expr: CronExpression,
    ref: datetime | None = None,
    sample: int = 100,
) -> RunStats:
    """Compute run statistics for *expr* using the next *sample* occurrences.

    Args:
        expr:   Parsed cron expression.
        ref:    Reference datetime (defaults to now).
        sample: Number of future runs to analyse.

    Returns:
        A :class:`RunStats` instance with computed metrics.

    Raises:
        ValueError: If *sample* is less than 2.
    """
    if sample < 2:
        raise ValueError("sample must be >= 2 to compute intervals")

    ref = ref or datetime.now().replace(second=0, microsecond=0)
    runs = next_runs(expr, n=sample, ref=ref)

    intervals: List[float] = [
        (runs[i + 1] - runs[i]).total_seconds() for i in range(len(runs) - 1)
    ]

    avg_gap = sum(intervals) / len(intervals)
    runs_per_hour = 3600.0 / avg_gap if avg_gap else 0.0
    runs_per_day = 86400.0 / avg_gap if avg_gap else 0.0

    return RunStats(
        expression=repr(expr),
        sample_size=sample,
        min_gap_seconds=min(intervals),
        max_gap_seconds=max(intervals),
        avg_gap_seconds=avg_gap,
        runs_per_hour=runs_per_hour,
        runs_per_day=runs_per_day,
        next_run=runs[0],
        intervals=intervals,
    )
