"""Group multiple cron expressions by their schedule category."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from cronlens.classifier import classify, ClassifyResult
from cronlens.parser import CronExpression, CronParseError


@dataclass
class GroupResult:
    """Holds expressions bucketed by their schedule category."""

    groups: Dict[str, List[str]] = field(default_factory=dict)
    invalid: List[str] = field(default_factory=list)

    def __str__(self) -> str:  # pragma: no cover
        lines: List[str] = []
        for category, exprs in sorted(self.groups.items()):
            lines.append(f"[{category}] ({len(exprs)})")
            for expr in exprs:
                lines.append(f"  {expr}")
        if self.invalid:
            lines.append(f"[invalid] ({len(self.invalid)})")
            for expr in self.invalid:
                lines.append(f"  {expr}")
        return "\n".join(lines)

    @property
    def category_names(self) -> List[str]:
        """Sorted list of category names present in this result."""
        return sorted(self.groups.keys())

    def expressions_for(self, category: str) -> List[str]:
        """Return expressions belonging to *category*, or empty list."""
        return self.groups.get(category, [])


def group(expressions: List[str]) -> GroupResult:
    """Classify each expression and bucket by category.

    Parameters
    ----------
    expressions:
        Raw cron expression strings to group.

    Returns
    -------
    GroupResult
        Mapping of category -> list of matching expressions, plus any
        expressions that failed to parse.
    """
    result = GroupResult()
    for raw in expressions:
        try:
            expr = CronExpression(raw)
        except CronParseError:
            result.invalid.append(raw)
            continue
        cr: ClassifyResult = classify(expr)
        result.groups.setdefault(cr.category, []).append(raw)
    return result
