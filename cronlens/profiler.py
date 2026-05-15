"""Profiler: analyse how busy a cron schedule is across a time window."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List

from .next_run import iter_next_runs
from .parser import CronExpression


@dataclass
class ProfileResult:
    expression: str
    window_hours: int
    total_runs: int
    runs_per_hour: Dict[int, int] = field(default_factory=dict)
    busiest_hour: int = 0
    quietest_hour: int = 0

    def __str__(self) -> str:  # pragma: no cover
        lines = [
            f"Profile: {self.expression}",
            f"Window : {self.window_hours}h",
            f"Runs   : {self.total_runs}",
            f"Busiest hour  : {self.busiest_hour:02d}:00 ({self.runs_per_hour.get(self.busiest_hour, 0)} runs)",
            f"Quietest hour : {self.quietest_hour:02d}:00 ({self.runs_per_hour.get(self.quietest_hour, 0)} runs)",
        ]
        return "\n".join(lines)


def profile(
    expr: CronExpression,
    ref: datetime | None = None,
    window_hours: int = 24,
) -> ProfileResult:
    """Count how many times *expr* fires in each hour of the window."""
    if window_hours < 1:
        raise ValueError("window_hours must be >= 1")

    ref = ref or datetime.now().replace(second=0, microsecond=0)
    end = ref + timedelta(hours=window_hours)

    runs_per_hour: Dict[int, int] = {h: 0 for h in range(24)}
    total = 0

    for dt in iter_next_runs(expr, ref=ref):
        if dt >= end:
            break
        runs_per_hour[dt.hour] += 1
        total += 1

    active_hours = {h: c for h, c in runs_per_hour.items() if c > 0}
    if active_hours:
        busiest = max(active_hours, key=lambda h: active_hours[h])
        quietest = min(active_hours, key=lambda h: active_hours[h])
    else:
        busiest = quietest = 0

    return ProfileResult(
        expression=repr(expr),
        window_hours=window_hours,
        total_runs=total,
        runs_per_hour=runs_per_hour,
        busiest_hour=busiest,
        quietest_hour=quietest,
    )
