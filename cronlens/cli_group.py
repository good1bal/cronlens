"""CLI sub-command: group — bucket cron expressions by schedule category."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from cronlens.grouper import group


_ANSI = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "cyan": "\033[36m",
    "red": "\033[31m",
    "yellow": "\033[33m",
}


def _color(text: str, code: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"{_ANSI[code]}{text}{_ANSI['reset']}"


def build_group_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "group",
        help="Group cron expressions by schedule category",
    )
    p.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="One or more cron expressions to group",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI colour output",
    )
    p.set_defaults(func=run_group)


def run_group(args: argparse.Namespace) -> int:
    use_color = not args.no_color
    result = group(args.expressions)

    for category in result.category_names:
        header = _color(f"[{category}]", "cyan", use_color)
        count = _color(f"({len(result.expressions_for(category))})", "bold", use_color)
        print(f"{header} {count}")
        for expr in result.expressions_for(category):
            print(f"  {expr}")

    if result.invalid:
        header = _color("[invalid]", "red", use_color)
        count = _color(f"({len(result.invalid)})", "bold", use_color)
        print(f"{header} {count}")
        for expr in result.invalid:
            print(f"  {_color(expr, 'yellow', use_color)}")
        return 1

    return 0
