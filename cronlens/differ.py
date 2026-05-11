"""Compare two cron expressions and summarize their differences."""

from dataclasses import dataclass
from typing import List

from cronlens.parser import CronExpression

FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]


@dataclass
class FieldDiff:
    field: str
    left: str
    right: str

    def __str__(self) -> str:
        return f"{self.field:>14}: {self.left!r:20} → {self.right!r}"


@dataclass
class CronDiff:
    left_expr: str
    right_expr: str
    changed_fields: List[FieldDiff]

    @property
    def is_identical(self) -> bool:
        return len(self.changed_fields) == 0

    def summary(self) -> str:
        if self.is_identical:
            return (
                f"'{self.left_expr}' and '{self.right_expr}' are identical."
            )
        lines = [
            f"Differences between '{self.left_expr}' and '{self.right_expr}':",
        ]
        for fd in self.changed_fields:
            lines.append(f"  {fd}")
        return "\n".join(lines)


def diff_expressions(left: str, right: str) -> CronDiff:
    """Parse *left* and *right* cron strings and return a CronDiff."""
    left_expr = CronExpression(left)
    right_expr = CronExpression(right)

    raw_left = left_expr.raw_fields   # list of 5 raw strings
    raw_right = right_expr.raw_fields

    changed: List[FieldDiff] = []
    for name, l_val, r_val in zip(FIELD_NAMES, raw_left, raw_right):
        if l_val != r_val:
            changed.append(FieldDiff(field=name, left=l_val, right=r_val))

    return CronDiff(
        left_expr=left,
        right_expr=right,
        changed_fields=changed,
    )
