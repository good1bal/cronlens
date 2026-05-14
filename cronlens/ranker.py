"""Rank and sort multiple cron expressions by various criteria."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from cronlens.parser import CronExpression
from cronlens.scorer import score, ScoreResult


SORTABLE_CRITERIA = ("complexity", "predictability", "score")


@dataclass
class RankEntry:
    expression: str
    parsed: CronExpression
    result: ScoreResult
    rank: int = 0

    def __str__(self) -> str:
        return (
            f"#{self.rank:>2}  {self.expression:<30}  "
            f"complexity={self.result.complexity}  "
            f"predictability={self.result.predictability}  "
            f"score={self.result.score}"
        )


@dataclass
class RankResult:
    entries: List[RankEntry] = field(default_factory=list)
    criterion: str = "score"
    ascending: bool = True

    def __str__(self) -> str:
        lines = [f"Ranked by '{self.criterion}' ({'asc' if self.ascending else 'desc'}):"]
        for entry in self.entries:
            lines.append(f"  {entry}")
        return "\n".join(lines)


def rank(
    expressions: List[str],
    criterion: str = "score",
    ascending: bool = True,
) -> RankResult:
    """Rank a list of cron expression strings by the given criterion.

    Parameters
    ----------
    expressions:
        Raw cron strings to rank.
    criterion:
        One of 'complexity', 'predictability', or 'score'.
    ascending:
        When True, lowest value comes first.

    Returns
    -------
    RankResult with entries sorted accordingly.
    """
    if criterion not in SORTABLE_CRITERIA:
        raise ValueError(
            f"Unknown criterion '{criterion}'. Choose from: {SORTABLE_CRITERIA}"
        )

    entries: List[RankEntry] = []
    for expr_str in expressions:
        parsed = CronExpression(expr_str)
        result = score(parsed)
        entries.append(RankEntry(expression=expr_str, parsed=parsed, result=result))

    entries.sort(
        key=lambda e: getattr(e.result, criterion),
        reverse=not ascending,
    )

    for i, entry in enumerate(entries, start=1):
        entry.rank = i

    return RankResult(entries=entries, criterion=criterion, ascending=ascending)
