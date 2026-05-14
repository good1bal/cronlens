"""Score a cron expression by complexity and predictability."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cronlens.parser import CronExpression

# Field names in order
_FIELDS = ("minute", "hour", "day", "month", "weekday")

# Weights per field — higher-frequency fields penalise complexity more
_COMPLEXITY_WEIGHTS = {
    "minute": 3,
    "hour": 2,
    "day": 1,
    "month": 1,
    "weekday": 1,
}


@dataclass
class ScoreResult:
    """Holds complexity and predictability scores for a cron expression."""

    expression: str
    complexity: int  # 0 (simple) – 100 (very complex)
    predictability: int  # 0 (chaotic) – 100 (perfectly regular)
    notes: list[str]

    def __str__(self) -> str:
        lines = [
            f"Expression : {self.expression}",
            f"Complexity  : {self.complexity}/100",
            f"Predictability: {self.predictability}/100",
        ]
        if self.notes:
            lines.append("Notes:")
            for note in self.notes:
                lines.append(f"  • {note}")
        return "\n".join(lines)


def _field_tokens(raw: str) -> list[str]:
    """Split a raw field string into its comma-separated tokens."""
    return [t.strip() for t in raw.split(",")]


def _token_complexity(token: str) -> int:
    """Return a complexity score (0-3) for a single token."""
    if token == "*":
        return 0
    if "/" in token:
        return 1
    if "-" in token:
        return 2
    return 3  # specific value


def score(expr: "CronExpression") -> ScoreResult:
    """Compute complexity and predictability scores for *expr*."""
    raw_fields = {
        "minute": expr.raw_minute,
        "hour": expr.raw_hour,
        "day": expr.raw_day,
        "month": expr.raw_month,
        "weekday": expr.raw_weekday,
    }

    notes: list[str] = []
    complexity_sum = 0
    max_possible = sum(3 * _COMPLEXITY_WEIGHTS[f] for f in _FIELDS)

    for field in _FIELDS:
        raw = raw_fields[field]
        tokens = _field_tokens(raw)
        token_score = sum(_token_complexity(t) for t in tokens)
        # Multiple comma-separated values add extra complexity
        if len(tokens) > 1:
            token_score += len(tokens) - 1
            notes.append(f"{field}: comma list with {len(tokens)} values")
        complexity_sum += token_score * _COMPLEXITY_WEIGHTS[field]

    if raw_fields["day"] != "*" and raw_fields["weekday"] != "*":
        complexity_sum += 5
        notes.append("Both day-of-month and weekday are constrained")

    complexity = min(100, int(complexity_sum / max_possible * 100))
    predictability = 100 - complexity

    if complexity <= 10:
        notes.insert(0, "Very simple schedule")
    elif complexity >= 70:
        notes.insert(0, "Highly complex schedule — consider splitting")

    return ScoreResult(
        expression=repr(expr),
        complexity=complexity,
        predictability=predictability,
        notes=notes,
    )
