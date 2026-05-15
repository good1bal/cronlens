"""Deduplicator: identify and remove duplicate cron expressions from a list."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict

from cronlens.parser import CronExpression, CronParseError


@dataclass
class DeduplicateResult:
    """Result of a deduplication pass over a list of cron expressions."""

    originals: List[str]
    unique: List[str]
    duplicates: Dict[str, List[str]]  # canonical -> list of duplicates
    invalid: List[str]

    @property
    def removed_count(self) -> int:
        return sum(len(v) for v in self.duplicates.values())

    @property
    def unique_count(self) -> int:
        return len(self.unique)

    def __str__(self) -> str:
        lines = [
            f"Expressions  : {len(self.originals)}",
            f"Unique       : {self.unique_count}",
            f"Duplicates   : {self.removed_count}",
            f"Invalid      : {len(self.invalid)}",
        ]
        if self.duplicates:
            lines.append("")
            lines.append("Duplicate groups:")
            for canonical, dupes in self.duplicates.items():
                lines.append(f"  {canonical!r} <- also seen as: {dupes}")
        if self.invalid:
            lines.append("")
            lines.append("Invalid expressions:")
            for inv in self.invalid:
                lines.append(f"  {inv!r}")
        return "\n".join(lines)


def _normalize(expr: str) -> str:
    """Parse and re-serialize an expression to get a canonical string form."""
    return repr(CronExpression(expr))


def deduplicate(expressions: List[str]) -> DeduplicateResult:
    """Return a DeduplicateResult for the given list of cron expression strings."""
    seen: Dict[str, str] = {}  # canonical -> first original
    duplicates: Dict[str, List[str]] = {}
    unique: List[str] = []
    invalid: List[str] = []

    for raw in expressions:
        try:
            canonical = _normalize(raw)
        except CronParseError:
            invalid.append(raw)
            continue

        if canonical not in seen:
            seen[canonical] = raw
            unique.append(raw)
        else:
            duplicates.setdefault(seen[canonical], []).append(raw)

    return DeduplicateResult(
        originals=list(expressions),
        unique=unique,
        duplicates=duplicates,
        invalid=invalid,
    )
