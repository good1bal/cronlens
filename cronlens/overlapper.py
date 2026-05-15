"""Detect time-window overlaps between two cron expressions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Tuple

from cronlens.parser import CronExpression
from cronlens.next_run import next_runs


@dataclass
class OverlapResult:
    expr_a: str
    expr_b: str
    window_hours: int
    shared_minutes: List[datetime] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.shared_minutes)

    @property
    def has_overlap(self) -> bool:
        return self.count > 0

    def __str__(self) -> str:
        lines = [
            f"Overlap: {self.expr_a!r} vs {self.expr_b!r}",
            f"Window : {self.window_hours}h",
            f"Shared : {self.count} minute(s)",
        ]
        if self.shared_minutes:
            lines.append("First  : " + self.shared_minutes[0].strftime("%Y-%m-%d %H:%M"))
        return "\n".join(lines)


def find_overlaps(
    expr_a: CronExpression,
    expr_b: CronExpression,
    ref: datetime | None = None,
    window_hours: int = 24,
) -> OverlapResult:
    """Return all minutes within *window_hours* where both expressions fire."""
    if window_hours < 1:
        raise ValueError("window_hours must be >= 1")

    ref = ref or datetime.now().replace(second=0, microsecond=0)
    n = window_hours * 60  # upper bound: one run per minute

    runs_a: List[datetime] = next_runs(expr_a, n=n, ref=ref)
    set_a = {dt.replace(second=0, microsecond=0) for dt in runs_a}

    runs_b: List[datetime] = next_runs(expr_b, n=n, ref=ref)
    set_b = {dt.replace(second=0, microsecond=0) for dt in runs_b}

    shared = sorted(set_a & set_b)

    return OverlapResult(
        expr_a=repr(expr_a),
        expr_b=repr(expr_b),
        window_hours=window_hours,
        shared_minutes=shared,
    )
