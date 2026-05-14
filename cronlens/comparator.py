"""Compare two cron expressions by their next-run schedules."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple

from .parser import CronExpression
from .next_run import next_runs


@dataclass
class CompareResult:
    expr_a: str
    expr_b: str
    shared: List[datetime]
    only_a: List[datetime]
    only_b: List[datetime]

    @property
    def overlap_count(self) -> int:
        return len(self.shared)

    @property
    def total_a(self) -> int:
        return len(self.shared) + len(self.only_a)

    @property
    def total_b(self) -> int:
        return len(self.shared) + len(self.only_b)

    @property
    def overlap_pct_a(self) -> float:
        return (self.overlap_count / self.total_a * 100) if self.total_a else 0.0

    @property
    def overlap_pct_b(self) -> float:
        return (self.overlap_count / self.total_b * 100) if self.total_b else 0.0

    def summary(self) -> str:
        lines = [
            f"Comparing: '{self.expr_a}'  vs  '{self.expr_b}'",
            f"  Shared runs   : {self.overlap_count}",
            f"  Only in first : {len(self.only_a)}",
            f"  Only in second: {len(self.only_b)}",
            f"  Overlap (A)   : {self.overlap_pct_a:.1f}%",
            f"  Overlap (B)   : {self.overlap_pct_b:.1f}%",
        ]
        return "\n".join(lines)


def compare(
    expr_a: CronExpression,
    expr_b: CronExpression,
    *,
    n: int = 60,
    ref: datetime | None = None,
) -> CompareResult:
    """Compare the next *n* runs of two expressions.

    Returns a :class:`CompareResult` with shared and exclusive run times.
    """
    if n < 1:
        raise ValueError("n must be >= 1")

    kwargs = {"ref": ref} if ref is not None else {}
    runs_a: List[datetime] = next_runs(expr_a, n, **kwargs)
    runs_b: List[datetime] = next_runs(expr_b, n, **kwargs)

    set_a = set(runs_a)
    set_b = set(runs_b)

    shared = sorted(set_a & set_b)
    only_a = sorted(set_a - set_b)
    only_b = sorted(set_b - set_a)

    return CompareResult(
        expr_a=repr(expr_a),
        expr_b=repr(expr_b),
        shared=shared,
        only_a=only_a,
        only_b=only_b,
    )
