"""CLI sub-command: heatmap — frequency grid across hours/days."""

from __future__ import annotations

import argparse
import sys

from cronlens.parser import CronExpression, CronParseError
from cronlens.heatmap import build_heatmap


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def build_heatmap_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = subparsers.add_parser(
        "heatmap",
        help="Show a run-frequency heatmap across hours and weekdays",
    )
    p.add_argument("expression", help="Cron expression (quote it)")
    p.add_argument(
        "--days",
        type=int,
        default=7,
        metavar="N",
        help="Window size in days (default: 7)",
    )
    p.add_argument("--no-color", action="store_true", help="Disable ANSI color")
    return p


def run_heatmap(args: argparse.Namespace) -> int:
    try:
        expr = CronExpression(args.expression)
    except CronParseError as exc:
        msg = f"Invalid expression: {exc}"
        print(_color(msg, "31") if not args.no_color else msg, file=sys.stderr)
        return 1

    if args.days < 1:
        msg = "--days must be >= 1"
        print(_color(msg, "31") if not args.no_color else msg, file=sys.stderr)
        return 1

    result = build_heatmap(expr, window_days=args.days)
    output = str(result)

    if not args.no_color:
        # Highlight the header line in bold
        lines = output.splitlines()
        lines[0] = _color(lines[0], "1")
        output = "\n".join(lines)

    print(output)
    return 0
