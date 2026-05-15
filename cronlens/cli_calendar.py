"""CLI sub-command: cronlens calendar <expression> [--weeks N] [--no-color]"""

from __future__ import annotations

import argparse
import sys

from cronlens.parser import CronExpression, CronParseError
from cronlens.calendar_view import build_calendar, DAY_NAMES

_RESET = "\033[0m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_BOLD = "\033[1m"


def _color(text: str, code: str, use_color: bool) -> str:
    return f"{code}{text}{_RESET}" if use_color else text


def build_calendar_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "calendar",
        help="Show a weekly calendar grid of when a cron expression fires.",
    )
    p.add_argument("expression", help="Cron expression (5 fields) or @alias")
    p.add_argument(
        "--weeks",
        type=int,
        default=1,
        metavar="N",
        help="Number of weeks to simulate (default: 1)",
    )
    p.add_argument("--no-color", action="store_true", help="Disable ANSI color output")


def run_calendar(args: argparse.Namespace, out=sys.stdout, err=sys.stderr) -> int:
    use_color = not getattr(args, "no_color", False)
    try:
        expr = CronExpression(args.expression)
    except CronParseError as exc:
        print(_color(f"Error: {exc}", _RED, use_color), file=err)
        return 1

    if args.weeks < 1:
        print(_color("Error: --weeks must be >= 1", _RED, use_color), file=err)
        return 1

    result = build_calendar(expr, weeks=args.weeks)
    pk = result.peak or 1

    header_line = _color(
        f"Calendar view for: {result.expression}  (over {args.weeks} week(s))",
        _BOLD,
        use_color,
    )
    print(header_line, file=out)
    hour_header = "     " + "".join(f"{h:>3}" for h in range(24))
    print(_color(hour_header, _BOLD, use_color), file=out)

    for dow, name in enumerate(DAY_NAMES):
        cells = ""
        for hour in range(24):
            v = result.grid[dow][hour]
            if v == 0:
                symbol = _color("  .", _RESET, use_color)
            elif v / pk < 0.5:
                symbol = _color("  +", _YELLOW, use_color)
            else:
                symbol = _color("  #", _GREEN, use_color)
            cells += symbol
        print(f"{name} {cells}", file=out)

    footer = f"Total fires: {result.total}  Peak slot: {result.peak}"
    print(_color(footer, _BOLD, use_color), file=out)
    return 0
