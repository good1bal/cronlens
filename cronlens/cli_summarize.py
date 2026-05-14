"""CLI sub-command: cronlens summarize — show run statistics for an expression."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from cronlens.parser import CronExpression, CronParseError
from cronlens.summarizer import summarize


def build_summarize_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:  # noqa: SLF001
    p = subparsers.add_parser(
        "summarize",
        help="Display aggregate run statistics for a cron expression.",
    )
    p.add_argument("expression", help="Cron expression (quote it!), e.g. '*/5 * * * *'")
    p.add_argument(
        "--sample",
        type=int,
        default=100,
        metavar="N",
        help="Number of future runs to analyse (default: 100).",
    )
    p.add_argument(
        "--ref",
        metavar="DATETIME",
        help="Reference datetime in ISO format, e.g. '2024-01-15T12:00'. Defaults to now.",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI color output.",
    )
    return p


def _label(text: str, color: bool) -> str:
    if color:
        return f"\033[1;36m{text}\033[0m"
    return text


def run_summarize(args: argparse.Namespace) -> int:
    """Entry point for the summarize sub-command.

    Returns an exit code (0 = success, non-zero = failure).
    """
    use_color = not getattr(args, "no_color", False)

    try:
        expr = CronExpression(args.expression)
    except CronParseError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    ref: datetime | None = None
    if args.ref:
        try:
            ref = datetime.fromisoformat(args.ref)
        except ValueError:
            print(f"Error: invalid --ref datetime '{args.ref}'", file=sys.stderr)
            return 1

    try:
        stats = summarize(expr, ref=ref, sample=args.sample)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    header = _label("=== Cron Run Statistics ===", use_color)
    print(header)
    print(stats)
    return 0
