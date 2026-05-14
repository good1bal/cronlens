"""CLI sub-command: cronlens export — dump cron info as JSON or text."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from cronlens.parser import CronExpression, CronParseError
from cronlens.exporter import export_json, export_text


def build_export_parser(sub: "argparse._SubParsersAction") -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = sub.add_parser(
        "export",
        help="Export cron expression metadata as JSON or plain text",
    )
    p.add_argument("expression", help="Cron expression (5 fields)")
    p.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        dest="fmt",
        help="Output format (default: json)",
    )
    p.add_argument(
        "--next",
        type=int,
        default=5,
        metavar="N",
        dest="next_n",
        help="Number of next runs to include (default: 5)",
    )
    p.add_argument(
        "--prev",
        type=int,
        default=5,
        metavar="N",
        dest="prev_n",
        help="Number of previous runs to include (default: 5)",
    )
    p.add_argument(
        "--ref",
        default=None,
        metavar="DATETIME",
        help="Reference datetime ISO-8601 (default: now)",
    )
    return p


def run_export(args: argparse.Namespace) -> int:
    try:
        expr = CronExpression(args.expression)
    except CronParseError as exc:
        print(f"Parse error: {exc}", file=sys.stderr)
        return 1

    ref: datetime | None = None
    if args.ref:
        try:
            ref = datetime.fromisoformat(args.ref).replace(second=0, microsecond=0)
        except ValueError:
            print(f"Invalid --ref datetime: {args.ref!r}", file=sys.stderr)
            return 1

    kwargs = dict(ref=ref, next_n=args.next_n, prev_n=args.prev_n)
    if args.fmt == "json":
        print(export_json(expr, **kwargs))  # type: ignore[arg-type]
    else:
        print(export_text(expr, **kwargs))  # type: ignore[arg-type]
    return 0
