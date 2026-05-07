"""Terminal visualizer: render next-run times in a human-readable table."""

from __future__ import annotations

from datetime import datetime
from typing import List

from cronlens.next_run import next_runs
from cronlens.parser import CronExpression

_HEADER = "{:<5}  {:<22}  {}"
_ROW = "{:<5}  {:<22}  {}"
_DATE_FMT = "%Y-%m-%d %H:%M"
_RELATIVE_UNITS = [
    (60, "minute"),
    (3600, "hour"),
    (86400, "day"),
]


def _relative_label(dt: datetime, now: datetime) -> str:
    """Return a short human-readable delta string, e.g. 'in 3 hours'."""
    delta = int((dt - now).total_seconds())
    if delta < 60:
        return "in <1 minute"
    for seconds, unit in reversed(_RELATIVE_UNITS):
        value = delta // seconds
        if value >= 1:
            plural = "s" if value != 1 else ""
            return f"in {value} {unit}{plural}"
    return "soon"


def render_next_runs(
    expr: CronExpression,
    n: int = 5,
    now: datetime | None = None,
    color: bool = True,
) -> str:
    """Return a formatted multi-line string showing the next *n* run times."""
    now = now or datetime.now()
    runs: List[datetime] = next_runs(expr, n=n, after=now)

    bold = "\033[1m" if color else ""
    cyan = "\033[36m" if color else ""
    reset = "\033[0m" if color else ""

    lines: List[str] = [
        f"{bold}Next {n} runs for: {cyan}{expr!r}{reset}",
        _HEADER.format("#", "Datetime", "Relative"),
        "-" * 50,
    ]
    for idx, dt in enumerate(runs, start=1):
        lines.append(_ROW.format(idx, dt.strftime(_DATE_FMT), _relative_label(dt, now)))
    return "\n".join(lines)
