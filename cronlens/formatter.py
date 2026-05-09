"""Formats cron expressions and their explanations into structured output."""

from __future__ import annotations

from typing import Optional

from cronlens.parser import CronExpression
from cronlens.explainer import explain


FIELD_LABELS = ["Minute", "Hour", "Day (month)", "Month", "Day (week)"]


def format_field_table(expr: CronExpression, color: bool = True) -> str:
    """Return a table showing each cron field and its raw value."""
    fields = [
        expr.minute_raw,
        expr.hour_raw,
        expr.dom_raw,
        expr.month_raw,
        expr.dow_raw,
    ]

    col_width = max(len(label) for label in FIELD_LABELS)
    val_width = max(len(v) for v in fields)

    sep = "+" + "-" * (col_width + 2) + "+" + "-" * (val_width + 2) + "+"
    header = "| {:<{}} | {:<{}} |".format("Field", col_width, "Value", val_width)

    lines = [sep, header, sep]
    for label, value in zip(FIELD_LABELS, fields):
        if color:
            value_display = f"\033[96m{value:<{val_width}}\033[0m"
            lines.append(f"| {{:<{}}} | {} |".format(col_width, value_display).format(label))
        else:
            lines.append("| {:<{}} | {:<{}} |".format(label, col_width, value, val_width))
    lines.append(sep)
    return "\n".join(lines)


def format_summary(expr: CronExpression, color: bool = True) -> str:
    """Return a human-readable summary block for the cron expression."""
    raw = str(expr)
    description = explain(expr)

    if color:
        raw_display = f"\033[93m{raw}\033[0m"
        desc_display = f"\033[92m{description}\033[0m"
    else:
        raw_display = raw
        desc_display = description

    lines = [
        f"Expression : {raw_display}",
        f"Meaning    : {desc_display}",
    ]
    return "\n".join(lines)


def format_full(expr: CronExpression, color: bool = True) -> str:
    """Return the full formatted output: summary + field table."""
    parts = [
        format_summary(expr, color=color),
        "",
        format_field_table(expr, color=color),
    ]
    return "\n".join(parts)
