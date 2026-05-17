"""CLI sub-command: cronlens pause — show quiet windows for a cron expression."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from cronlens.parser import CronExpression, CronParseError
from cronlens.pauser import find_pauses


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def build_pause_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = subparsers.add_parser(
        "pause",
        help="Find quiet windows (gaps) in a cron schedule.",
    )
    p.add_argument("expression", help="Cron expression (quote it).")
    p.add_argument(
        "--hours",
        type=int,
        default=24,
        metavar="N",
        help="Look-ahead window in hours (default: 24).",
    )
    p.add_argument(
        "--min-gap",
        type=int,
        default=60,
        metavar="M",
        dest="min_gap",
        help="Minimum gap in minutes to report (default: 60).",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI colour output.",
    )
    return p


def run_pause(args: argparse.Namespace, out=sys.stdout, err=sys.stderr) -> int:
    try:
        expr = CronExpression(args.expression)
    except CronParseError as exc:
        print(_color(f"Error: {exc}", "31"), file=err)
        return 1

    try:
        result = find_pauses(
            expr,
            ref=datetime.now().replace(second=0, microsecond=0),
            window_hours=args.hours,
            min_gap_minutes=args.min_gap,
        )
    except ValueError as exc:
        print(_color(f"Error: {exc}", "31"), file=err)
        return 1

    use_color = not args.no_color

    header = f"Quiet windows for: {args.expression}"
    print((_color(header, "1;36") if use_color else header), file=out)
    print(file=out)

    if not result.windows:
        msg = f"No quiet windows >= {args.min_gap} min found in the next {args.hours}h."
        print((_color(msg, "33") if use_color else msg), file=out)
        return 0

    for w in result.windows:
        label = str(w)
        print((_color(label, "32") if use_color else label), file=out)

    print(file=out)
    summary = f"Total quiet time: {result.total_quiet_minutes} min across {len(result.windows)} gap(s)."
    print((_color(summary, "1") if use_color else summary), file=out)
    return 0
