"""CLI sub-command: cronlens streak — show run-day / run-hour streaks."""

from __future__ import annotations

import argparse
import sys

from cronlens.parser import CronExpression, CronParseError
from cronlens.streaker import find_streaks


def _color(text: str, code: str, use_color: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if use_color else text


def build_streak_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = subparsers.add_parser("streak", help="Show consecutive run-day and run-hour streaks")
    p.add_argument("expression", help="Cron expression (quote it)")
    p.add_argument(
        "--days",
        type=int,
        default=30,
        metavar="N",
        help="History window in days (default: 30)",
    )
    p.add_argument("--no-color", action="store_true", help="Disable ANSI color output")
    return p


def run_streak(args: argparse.Namespace) -> int:
    use_color = not args.no_color
    try:
        expr = CronExpression(args.expression)
    except CronParseError as exc:
        print(_color(f"Error: {exc}", "31", use_color), file=sys.stderr)
        return 1

    if args.days < 1:
        print(_color("Error: --days must be >= 1", "31", use_color), file=sys.stderr)
        return 1

    result = find_streaks(expr, window_days=args.days)

    header = _color("=== Streak Report ===", "1;36", use_color)
    print(header)
    print(_color(f"Expression : {result.expression}", "33", use_color))
    print(f"Window     : {result.window_days} days")
    print(f"Active days: {result.active_days}")
    print(f"Active hrs : {result.active_hours}")
    print(
        "Longest day streak : "
        + _color(str(result.longest_day_streak), "1;32", use_color)
        + " day(s)"
    )
    print(
        "Longest hour streak: "
        + _color(str(result.longest_hour_streak), "1;32", use_color)
        + " hour(s)"
    )
    return 0
