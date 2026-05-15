"""CLI sub-command: forecast — show how many times a cron fires in a future window."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from cronlens.parser import CronExpression, CronParseError
from cronlens.forecaster import forecast

_ANSI = {
    "green": "\033[32m",
    "yellow": "\033[33m",
    "cyan": "\033[36m",
    "reset": "\033[0m",
}


def _color(text: str, code: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"{_ANSI.get(code, '')}{text}{_ANSI['reset']}"


def build_forecast_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "forecast",
        help="Forecast run count for a cron expression over a future window",
    )
    p.add_argument("expression", help="Cron expression (5-field)")
    p.add_argument(
        "--hours",
        type=int,
        default=24,
        metavar="N",
        help="Forecast window in hours (default: 24)",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colour output",
    )
    p.add_argument(
        "--list",
        action="store_true",
        dest="list_runs",
        help="Print each scheduled run timestamp",
    )
    p.set_defaults(func=run_forecast)


def run_forecast(args: argparse.Namespace) -> int:
    use_color = not args.no_color

    try:
        expr = CronExpression(args.expression)
    except CronParseError as exc:
        print(_color(f"Error: {exc}", "yellow", use_color), file=sys.stderr)
        return 1

    try:
        result = forecast(expr, window_hours=args.hours)
    except ValueError as exc:
        print(_color(f"Error: {exc}", "yellow", use_color), file=sys.stderr)
        return 1

    print(_color(str(result), "cyan", use_color))

    if args.list_runs:
        print()
        print(_color(f"Scheduled runs ({result.count}):", "green", use_color))
        for dt in result.runs:
            print(f"  {dt.strftime('%Y-%m-%d %H:%M')}")

    return 0
