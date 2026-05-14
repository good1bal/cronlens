"""Main CLI entry-point for cronlens."""

from __future__ import annotations

import argparse
import sys

from cronlens.parser import CronExpression, CronParseError
from cronlens.formatter import format_full
from cronlens.visualizer import render_next_runs, render_prev_runs
from cronlens.cli_validate import build_validate_parser, run_validate, run_lint
from cronlens.cli_export import build_export_parser, run_export


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronlens",
        description="Human-readable cron expression parser and next-run visualizer",
    )
    sub = parser.add_subparsers(dest="command")

    # show — default rich view
    show = sub.add_parser("show", help="Show cron expression details and next runs")
    show.add_argument("expression", help="Cron expression (5 fields)")
    show.add_argument("--next", type=int, default=5, metavar="N", dest="next_n")
    show.add_argument("--prev", type=int, default=0, metavar="N", dest="prev_n")
    show.add_argument("--no-color", action="store_true")

    # validate / lint
    build_validate_parser(sub)

    # export
    build_export_parser(sub)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None or args.command == "show":
        if not hasattr(args, "expression"):
            parser.print_help()
            return 0
        try:
            expr = CronExpression(args.expression)
        except CronParseError as exc:
            print(f"Parse error: {exc}", file=sys.stderr)
            return 1
        print(format_full(expr))
        color = not args.no_color
        if args.next_n > 0:
            print(render_next_runs(expr, n=args.next_n, color=color))
        if args.prev_n > 0:
            print(render_prev_runs(expr, n=args.prev_n, color=color))
        return 0

    if args.command == "validate":
        return run_validate(args)
    if args.command == "lint":
        return run_lint(args)
    if args.command == "export":
        return run_export(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
