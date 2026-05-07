"""Command-line entry point for cronlens."""

from __future__ import annotations

import argparse
import sys

from cronlens.parser import CronExpression, CronParseError
from cronlens.visualizer import render_next_runs


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cronlens",
        description="Human-readable cron expression parser and next-run visualizer.",
    )
    p.add_argument(
        "expression",
        help='Cron expression in quotes, e.g. "*/15 9-17 * * 1-5"',
    )
    p.add_argument(
        "-n",
        "--count",
        type=int,
        default=5,
        metavar="N",
        help="Number of upcoming run times to display (default: 5).",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI color output.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        expr = CronExpression(args.expression)
    except CronParseError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    output = render_next_runs(expr, n=args.count, color=not args.no_color)
    print(output)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
