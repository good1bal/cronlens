"""Detect quiet windows — contiguous periods with no scheduled runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

from cronlens.next_run import iter_next_runs
from cronlens.parser import CronExpression


@dataclass
class QuietWindow:
    """A contiguous gap between two consecutive cron runs."""

    start: datetime
    end: datetime

    @property
    def duration_minutes(self) -> int:
        delta = self.end - self.start
        return int(delta.total_seconds() // 60)

    def __str__(self) -> str:  # pragma: no cover
        fmt = "%Y-%m-%d %H:%M"
        return (
            f"{self.start.strftime(fmt)} → {self.end.strftime(fmt)}"
            f"  ({self.duration_minutes} min)"
        )


@dataclass
class PauseResult:
    """Collection of quiet windows found within a look-ahead window."""

    expression: str
    window_hours: int
    windows: List[QuietWindow] = field(default_factory=list)

    @property
    def longest(self) -> QuietWindow | None:
        return max(self.windows, key=lambda w: w.duration_minutes, default=None)

    @property
    def total_quiet_minutes(self) -> int:
        return sum(w.duration_minutes for w in self.windows)

    def __str__(self) -> str:
        lines = [
            f"Expression : {self.expression}",
            f"Window     : {self.window_hours}h",
            f"Quiet gaps : {len(self.windows)}",
            f"Total quiet: {self.total_quiet_minutes} min",
        ]
        if self.longest:
            lines.append(f"Longest gap: {self.longest.duration_minutes} min")
        for w in self.windows:
            lines.append(f"  {w}")
        return "\n".join(lines)


def find_pauses(
    expr: CronExpression,
    *,
    ref: datetime | None = None,
    window_hours: int = 24,
    min_gap_minutes: int = 60,
) -> PauseResult:
    """Return all quiet windows longer than *min_gap_minutes* within *window_hours*."""
    if window_hours < 1:
        raise ValueError("window_hours must be >= 1")
    if min_gap_minutes < 1:
        raise ValueError("min_gap_minutes must be >= 1")

    ref = ref or datetime.now().replace(second=0, microsecond=0)
    horizon = ref + timedelta(hours=window_hours)

    runs = []
    for run in iter_next_runs(expr, ref=ref):
        if run > horizon:
            break
        runs.append(run)

    result = PauseResult(expression=repr(expr), window_hours=window_hours)
    for i in range(len(runs) - 1):
        gap = int((runs[i + 1] - runs[i]).total_seconds() // 60)
        if gap >= min_gap_minutes:
            result.windows.append(QuietWindow(start=runs[i], end=runs[i + 1]))
    return result
