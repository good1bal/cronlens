"""CLI sub-command: rank — compare and rank multiple cron expressions."""

from __future__ import annotations

import argparse
import sys
from typing import List

from cronlens.parser import CronParseError
from cronlens.ranker import rank, SORTABLE_CRITERIA


ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_RED = "\033[31m"


def _color(text: str, code: str, use_color: bool) -> str:
    return f"{code}{text}{ANSI_RESET}" if use_color else text


def build_rank_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "rank",
        help="Rank multiple cron expressions by complexity, predictability, or score.",
    )
    p.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="Two or more cron expressions to rank.",
    )
    p.add_argument(
        "--by",
        dest="criterion",
        choices=list(SORTABLE_CRITERIA),
        default="score",
        help="Ranking criterion (default: score).",
    )
    p.add_argument(
        "--desc",
        action="store_true",
        default=False,
        help="Sort in descending order (default: ascending).",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI colour output.",
    )
    return p


def run_rank(args: argparse.Namespace) -> int:
    use_color = not args.no_color
    ascending = not args.desc

    try:
        result = rank(args.expressions, criterion=args.criterion, ascending=ascending)
    except CronParseError as exc:
        print(
            _color(f"Parse error: {exc}", ANSI_RED, use_color),
            file=sys.stderr,
        )
        return 1
    except ValueError as exc:
        print(_color(str(exc), ANSI_RED, use_color), file=sys.stderr)
        return 1

    direction = "ascending" if ascending else "descending"
    header = _color(
        f"Ranked by '{args.criterion}' ({direction}):",
        ANSI_BOLD,
        use_color,
    )
    print(header)

    for entry in result.entries:
        rank_label = _color(f"#{entry.rank:>2}", ANSI_GREEN, use_color)
        expr_label = _color(entry.expression, ANSI_BOLD, use_color)
        details = (
            f"complexity={entry.result.complexity}  "
            f"predictability={entry.result.predictability}  "
            f"score={entry.result.score}"
        )
        print(f"  {rank_label}  {expr_label:<30}  {details}")

    return 0
