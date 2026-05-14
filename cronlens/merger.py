"""Merge two cron expressions into a unified schedule covering both."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Set

from cronlens.parser import CronExpression

FIELD_NAMES = ["minute", "hour", "day", "month", "weekday"]


def _merge_field(a: str, b: str) -> str:
    """Merge two individual cron fields into a combined field string."""
    if a == "*" or b == "*":
        return "*"
    parts_a: Set[str] = set(a.split(","))
    parts_b: Set[str] = set(b.split(","))
    merged = sorted(parts_a | parts_b, key=lambda x: int(x) if x.isdigit() else 0)
    return ",".join(merged)


@dataclass
class MergeResult:
    """Result of merging two cron expressions."""

    expr_a: CronExpression
    expr_b: CronExpression
    merged: CronExpression
    lossy_fields: List[str]

    def is_lossless(self) -> bool:
        """Return True if the merge preserved all constraints exactly."""
        return len(self.lossy_fields) == 0

    def summary(self) -> str:
        lines = [
            f"Expression A : {self.expr_a}",
            f"Expression B : {self.expr_b}",
            f"Merged       : {self.merged}",
        ]
        if self.lossy_fields:
            lines.append(f"Note: wildcard expansion applied to: {', '.join(self.lossy_fields)}")
        else:
            lines.append("Merge is lossless — no wildcard expansion needed.")
        return "\n".join(lines)


def merge(expr_a: CronExpression, expr_b: CronExpression) -> MergeResult:
    """Merge two CronExpressions and return a MergeResult."""
    raw_a = [expr_a.minute, expr_a.hour, expr_a.day, expr_a.month, expr_a.weekday]
    raw_b = [expr_b.minute, expr_b.hour, expr_b.day, expr_b.month, expr_b.weekday]

    merged_fields: List[str] = []
    lossy: List[str] = []

    for name, fa, fb in zip(FIELD_NAMES, raw_a, raw_b):
        result = _merge_field(fa, fb)
        if result == "*" and not (fa == "*" and fb == "*"):
            lossy.append(name)
        merged_fields.append(result)

    merged_expr = CronExpression(" ".join(merged_fields))
    return MergeResult(
        expr_a=expr_a,
        expr_b=expr_b,
        merged=merged_expr,
        lossy_fields=lossy,
    )
