"""Export cron expressions and their metadata to JSON or plain-text formats."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from cronlens.parser import CronExpression
from cronlens.explainer import explain
from cronlens.next_run import next_runs
from cronlens.history import prev_runs


def _dt_iso(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


def export_json(
    expr: CronExpression,
    *,
    ref: datetime | None = None,
    next_n: int = 5,
    prev_n: int = 5,
    indent: int = 2,
) -> str:
    """Return a JSON string describing *expr* with next/prev run times."""
    ref = ref or datetime.now().replace(second=0, microsecond=0)
    payload: dict[str, Any] = {
        "expression": repr(expr),
        "explanation": explain(expr),
        "fields": {
            "minute": expr.minute,
            "hour": expr.hour,
            "day": expr.day,
            "month": expr.month,
            "weekday": expr.weekday,
        },
        "reference": _dt_iso(ref),
        "next_runs": [_dt_iso(dt) for dt in next_runs(expr, n=next_n, ref=ref)],
        "prev_runs": [_dt_iso(dt) for dt in prev_runs(expr, n=prev_n, ref=ref)],
    }
    return json.dumps(payload, indent=indent)


def export_text(
    expr: CronExpression,
    *,
    ref: datetime | None = None,
    next_n: int = 5,
    prev_n: int = 5,
) -> str:
    """Return a plain-text summary of *expr*."""
    ref = ref or datetime.now().replace(second=0, microsecond=0)
    lines = [
        f"Expression : {repr(expr)}",
        f"Meaning    : {explain(expr)}",
        f"Reference  : {_dt_iso(ref)}",
        "",
        "Next runs:",
    ]
    for dt in next_runs(expr, n=next_n, ref=ref):
        lines.append(f"  {_dt_iso(dt)}")
    lines.append("")
    lines.append("Previous runs:")
    for dt in prev_runs(expr, n=prev_n, ref=ref):
        lines.append(f"  {_dt_iso(dt)}")
    return "\n".join(lines)
