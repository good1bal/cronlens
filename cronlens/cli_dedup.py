"""CLI sub-command: cronlens dedup — deduplicate a list of cron expressions."""

from __future__ import annotations

import argparse
import sys
from typing import List

from cronlens.deduplicator import deduplicate


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def build_dedup_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "dedup",
        help="Identify and remove duplicate cron expressions.",
    )
    p.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="Two or more cron expressions to deduplicate.",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI colour output.",
    )
    p.add_argument(
        "--unique-only",
        action="store_true",
        default=False,
        help="Print only the unique expressions, one per line.",
    )
    return p


def run_dedup(args: argparse.Namespace) -> int:
    result = deduplicate(args.expressions)
    use_color = not args.no_color

    if args.unique_only:
        for expr in result.unique:
            print(expr)
        return 0

    header = "cronlens dedup"
    if use_color:
        header = _color(header, "1;36")
    print(header)
    print()

    for line in str(result).splitlines():
        if use_color and line.startswith("Duplicate"):
            print(_color(line, "1;33"))
        elif use_color and line.startswith("Invalid"):
            print(_color(line, "1;31"))
        else:
            print(line)

    if result.invalid:
        return 1
    return 0
