"""Format cron expressions and their metadata for terminal display."""

from __future__ import annotations

from cronlens.parser import CronExpression
from cronlens.explainer import explain

FIELD_LABELS = ["Minute", "Hour", "Day", "Month", "Weekday"]


def format_field_table(expr: CronExpression) -> str:
    """Return a plain-text table of each cron field and its raw value."""
    raw = [expr.minute, expr.hour, expr.day, expr.month, expr.weekday]
    width = max(len(label) for label in FIELD_LABELS)
    lines = [f"{'Field':<{width}}  Value"]
    lines.append("-" * (width + 10))
    for label, value in zip(FIELD_LABELS, raw):
        lines.append(f"{label:<{width}}  {value}")
    return "\n".join(lines)


def format_summary(expr: CronExpression) -> str:
    """Return a one-line human-readable summary of the expression."""
    meaning = explain(expr)
    return f"Expression : {expr}\nMeaning    : {meaning}"


def format_full(expr: CronExpression) -> str:
    """Return a full formatted block combining summary and field table."""
    lines = [
        format_summary(expr),
        "",
        format_field_table(expr),
    ]
    return "\n".join(lines)


def format_merge_result(merge_result) -> str:  # type: ignore[type-arg]
    """Format a MergeResult for terminal display."""
    from cronlens.merger import MergeResult  # local import to avoid cycles

    lines = [
        "=== Cron Merge Result ===",
        "",
        f"Expression A : {merge_result.expr_a}",
        f"Expression B : {merge_result.expr_b}",
        f"Merged       : {merge_result.merged}",
        "",
        f"Merged meaning: {explain(merge_result.merged)}",
    ]
    if merge_result.lossy_fields:
        lines.append(f"\n⚠  Lossy fields (wildcard expanded): {', '.join(merge_result.lossy_fields)}")
    else:
        lines.append("\n✓  Merge is lossless.")
    return "\n".join(lines)
