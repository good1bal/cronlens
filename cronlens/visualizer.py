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
    bold = _ANSI_BOLD if color else ""
    reset = _ANSI_RESET if color else ""
    green = _ANSI_GREEN if color else ""
    dim = _ANSI_DIM if color else ""
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
    bold = _ANSI_BOLD if color else ""
    reset = _ANSI_RESET if color else ""
    cyan = _ANSI_CYAN if color else ""
    dim = _ANSI_DIM if color else ""
    lines = [f"{bold}Previous {n} runs:{reset}"]
    for dt in runs:
        label = _relative_label(dt, ref)
        ts = dt.strftime("%Y-%m-%d %H:%M")
        lines.append(f"  {cyan}{ts}{reset}  {dim}({label} ago){reset}")
    return "\n".join(lines)
