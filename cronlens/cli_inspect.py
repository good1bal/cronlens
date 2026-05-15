"""CLI sub-command: inspect — show resolved values for each cron field."""

from __future__ import annotations

import argparse
import sys
from typing import List

from cronlens.inspector import inspect, InspectResult
from cronlens.parser import CronParseError

_ANSI = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "green": "\033[32m",
    "red": "\033[31m",
    "cyan": "\033[36m",
    "yellow": "\033[33m",
}


def _color(text: str, *codes: str, use_color: bool = True) -> str:
    if not use_color:
        return text
    prefix = "".join(_ANSI[c] for c in codes)
    return f"{prefix}{text}{_ANSI['reset']}"


def build_inspect_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "inspect",
        help="Show the resolved integer values for each field of a cron expression.",
    )
    p.add_argument("expression", help="Cron expression (quote if it contains spaces).")
    p.add_argument("--no-color", action="store_true", help="Disable ANSI color output.")
    return p


def run_inspect(args: argparse.Namespace) -> int:
    use_color = not getattr(args, "no_color", False)

    try:
        result: InspectResult = inspect(args.expression)
    except CronParseError as exc:
        print(_color(f"Error: {exc}", "red", use_color=use_color), file=sys.stderr)
        return 1

    header = _color(f"Inspection: {result.expression}", "bold", "cyan", use_color=use_color)
    print(header)
    col_heads = f"  {'Field':<10} {'Token':<20} Resolved values"
    print(_color(col_heads, "bold", use_color=use_color))
    print("  " + "-" * 58)

    for fi in result.fields:
        name_str = _color(f"{fi.name:<10}", "yellow", use_color=use_color)
        raw_str = _color(f"{fi.raw:<20}", "green", use_color=use_color)
        vals_str = ", ".join(str(v) for v in fi.values)
        print(f"  {name_str} {raw_str} {vals_str}")

    return 0
