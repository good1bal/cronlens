"""Forecast how many times a cron expression will fire within a future window."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

from cronlens.parser import CronExpression
from cronlens.next_run import iter_next_runs


@dataclass
class ForecastResult:
    """Holds forecast data for a cron expression over a future window."""

    expression: str
    window_hours: int
    runs: List[datetime]

    @property
    def count(self) -> int:
        return len(self.runs)

    @property
    def first_run(self) -> datetime | None:
        return self.runs[0] if self.runs else None

    @property
    def last_run(self) -> datetime | None:
        return self.runs[-1] if self.runs else None

    @property
    def runs_per_hour(self) -> float:
        if self.window_hours == 0:
            return 0.0
        return round(self.count / self.window_hours, 2)

    def __str__(self) -> str:
        lines = [
            f"Expression : {self.expression}",
            f"Window     : {self.window_hours}h",
            f"Total runs : {self.count}",
            f"Runs/hour  : {self.runs_per_hour}",
        ]
        if self.first_run:
            lines.append(f"First run  : {self.first_run.strftime('%Y-%m-%d %H:%M')}")
        if self.last_run and self.last_run != self.first_run:
            lines.append(f"Last run   : {self.last_run.strftime('%Y-%m-%d %H:%M')}")
        return "\n".join(lines)


def forecast(
    expr: CronExpression,
    window_hours: int = 24,
    ref: datetime | None = None,
) -> ForecastResult:
    """Return a ForecastResult for *expr* over the next *window_hours* hours."""
    if window_hours < 1:
        raise ValueError("window_hours must be >= 1")

    ref = ref or datetime.now().replace(second=0, microsecond=0)
    deadline = ref + timedelta(hours=window_hours)

    runs: List[datetime] = []
    for dt in iter_next_runs(expr, ref=ref):
        if dt >= deadline:
            break
        runs.append(dt)

    return ForecastResult(
        expression=repr(expr),
        window_hours=window_hours,
        runs=runs,
    )
