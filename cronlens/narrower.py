"""Narrow a cron expression to a specific time window.

Given a cron expression and a datetime range [start, end], returns all
matching run times that fall within that window.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from cronlens.parser import CronExpression, CronParseError
from cronlens.next_run import iter_next_runs


@dataclass
class NarrowResult:
    expression: str
    start: datetime
    end: datetime
    runs: List[datetime] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.runs)

    @property
    def first_run(self) -> datetime | None:
        return self.runs[0] if self.runs else None

    @property
    def last_run(self) -> datetime | None:
        return self.runs[-1] if self.runs else None

    def __str__(self) -> str:
        lines = [
            f"Expression : {self.expression}",
            f"Window     : {self.start.strftime('%Y-%m-%d %H:%M')} "
            f"→ {self.end.strftime('%Y-%m-%d %H:%M')}",
            f"Runs found : {self.count}",
        ]
        if self.first_run:
            lines.append(f"First run  : {self.first_run.strftime('%Y-%m-%d %H:%M')}")
        if self.last_run and self.last_run != self.first_run:
            lines.append(f"Last run   : {self.last_run.strftime('%Y-%m-%d %H:%M')}")
        if self.runs:
            lines.append("")
            for dt in self.runs:
                lines.append(f"  {dt.strftime('%Y-%m-%d %H:%M')}")
        return "\n".join(lines)


def narrow(
    expression: str,
    start: datetime,
    end: datetime,
) -> NarrowResult:
    """Return all runs of *expression* in the half-open interval [start, end)."""
    if end <= start:
        raise ValueError("end must be after start")

    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        raise ValueError(str(exc)) from exc

    # Estimate an upper bound for the number of minutes in the window so we
    # never spin forever; iter_next_runs will stop naturally once past end.
    window_minutes = int((end - start).total_seconds() / 60) + 2

    runs: List[datetime] = []
    for dt in iter_next_runs(expr, ref=start, n=window_minutes):
        if dt >= end:
            break
        runs.append(dt)

    return NarrowResult(
        expression=expression,
        start=start,
        end=end,
        runs=runs,
    )
