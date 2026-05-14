"""Terminal visualizer for next-run (and previous-run) schedules."""

from __future__ import annotations

from datetime import datetime
from typing import List

from cronlens.parser import CronExpression
from cronlens.next_run import next_runs
from cronlens.history import prev_runs

_ANSI_GREEN = "\033[32m"
_ANSI_CYAN = "\033[36m"
_ANSI_DIM = "\033[2m"
_ANSI_RESET = "\033[0m"
_ANSI_BOLD = "\033[1m"


def _relative_label(dt: datetime, ref: datetime) -> str:
    """Return a human-readable relative label for *dt* compared to *ref*."""
    delta = abs((dt - ref).total_seconds())
    if delta < 60:
        return "< 1 minute"
    minutes = int(delta // 60)
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    hours = int(minutes // 60)
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''}"
    days = int(hours // 24)
    return f"{days} day{'s' if days != 1 else ''}"


def _color_codes(color: bool) -> tuple[str, str, str, str, str]:
    """Return a tuple of (bold, reset, green, cyan, dim) ANSI codes.

    When *color* is ``False`` all codes are empty strings so the output
    remains plain text suitable for piping or logging.
    """
    if color:
        return _ANSI_BOLD, _ANSI_RESET, _ANSI_GREEN, _ANSI_CYAN, _ANSI_DIM
    return "", "", "", "", ""


def render_next_runs(
    expr: CronExpression,
    n: int = 5,
    ref: datetime | None = None,
    color: bool = True,
) -> str:
    """Render a table of the next *n* scheduled run times."""
    if ref is None:
        ref = datetime.now()
    runs = next_runs(expr, n=n, ref=ref)
    bold, reset, green, _, dim = _color_codes(color)
    lines = [f"{bold}Next {n} runs:{reset}"]
    for dt in runs:
        label = _relative_label(dt, ref)
        ts = dt.strftime("%Y-%m-%d %H:%M")
        lines.append(f"  {green}{ts}{reset}  {dim}(in {label}){reset}")
    return "\n".join(lines)


def render_prev_runs(
    expr: CronExpression,
    n: int = 5,
    ref: datetime | None = None,
    color: bool = True,
) -> str:
    """Render a table of the previous *n* scheduled run times."""
    if ref is None:
        ref = datetime.now()
    runs = prev_runs(expr, n=n, ref=ref)
    bold, reset, _, cyan, dim = _color_codes(color)
    lines = [f"{bold}Previous {n} runs:{reset}"]
    for dt in runs:
        label = _relative_label(dt, ref)
        ts = dt.strftime("%Y-%m-%d %H:%M")
        lines.append(f"  {cyan}{ts}{reset}  {dim}({label} ago){reset}")
    return "\n".join(lines)
