"""CLI sub-command: cronlens profile <expression> [--hours N] [--no-color]."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from .aliaser import is_alias, resolve
from .parser import CronExpression, CronParseError
from .profiler import profile

_ANSI = {
    "green": "\033[32m",
    "yellow": "\033[33m",
    "cyan": "\033[36m",
    "bold": "\033[1m",
    "reset": "\033[0m",
}


def _color(text: str, code: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"{_ANSI[code]}{text}{_ANSI['reset']}"


def build_profile_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "profile",
        help="Show run-frequency profile across a time window",
    )
    p.add_argument("expression", help="Cron expression (quote if needed)")
    p.add_argument(
        "--hours",
        type=int,
        default=24,
        metavar="N",
        help="Window size in hours (default: 24)",
    )
    p.add_argument("--no-color", action="store_true", help="Disable ANSI colour")


def run_profile(args: argparse.Namespace) -> int:
    raw = args.expression
    if is_alias(raw):
        raw = resolve(raw)

    try:
        expr = CronExpression(raw)
    except CronParseError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    use_color = not args.no_color
    result = profile(expr, ref=datetime.now().replace(second=0, microsecond=0), window_hours=args.hours)

    print(_color(f"Profile for: {result.expression}", "bold", use_color))
    print(_color(f"Window: {result.window_hours}h  |  Total runs: {result.total_runs}", "cyan", use_color))
    print()

    max_runs = max(result.runs_per_hour.values(), default=1) or 1
    bar_width = 30

    for hour in range(24):
        count = result.runs_per_hour.get(hour, 0)
        filled = int(bar_width * count / max_runs) if max_runs else 0
        bar = "█" * filled + "░" * (bar_width - filled)
        label = f"{hour:02d}:00"
        if count == max(result.runs_per_hour.values(), default=0) and count > 0:
            bar_str = _color(bar, "green", use_color)
        elif count > 0:
            bar_str = _color(bar, "yellow", use_color)
        else:
            bar_str = bar
        print(f"  {label}  {bar_str}  {count}")

    return 0
