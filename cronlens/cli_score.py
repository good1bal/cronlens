"""CLI sub-command: score — display complexity/predictability scores."""

from __future__ import annotations

import argparse
import sys

from cronlens.aliaser import is_alias, resolve
from cronlens.parser import CronExpression, CronParseError
from cronlens.scorer import score


def build_score_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    """Register the *score* sub-command and return its parser."""
    p = subparsers.add_parser(
        "score",
        help="Score a cron expression for complexity and predictability",
        description="Analyse how complex and predictable a cron expression is.",
    )
    p.add_argument(
        "expression",
        help="Cron expression (quoted) or @alias",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI colour output",
    )
    p.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Emit result as JSON",
    )
    return p


def _color_bar(value: int, use_color: bool) -> str:
    """Return a simple ASCII bar with optional colour coding."""
    filled = int(value / 10)
    bar = "█" * filled + "░" * (10 - filled)
    if not use_color:
        return bar
    if value <= 30:
        code = "\033[32m"  # green
    elif value <= 60:
        code = "\033[33m"  # yellow
    else:
        code = "\033[31m"  # red
    return f"{code}{bar}\033[0m"


def run_score(args: argparse.Namespace, out=sys.stdout, err=sys.stderr) -> int:
    """Execute the score sub-command; return an exit code."""
    raw = args.expression
    if is_alias(raw):
        try:
            raw = resolve(raw)
        except Exception as exc:  # noqa: BLE001
            print(f"Error: {exc}", file=err)
            return 1

    try:
        expr = CronExpression(raw)
    except CronParseError as exc:
        print(f"Parse error: {exc}", file=err)
        return 1

    result = score(expr)

    if args.json:
        import json
        payload = {
            "expression": result.expression,
            "complexity": result.complexity,
            "predictability": result.predictability,
            "notes": result.notes,
        }
        print(json.dumps(payload, indent=2), file=out)
        return 0

    use_color = not args.no_color
    print(f"Expression     : {result.expression}", file=out)
    print(f"Complexity     : {result.complexity:>3}/100  {_color_bar(result.complexity, use_color)}", file=out)
    print(f"Predictability : {result.predictability:>3}/100  {_color_bar(result.predictability, use_color)}", file=out)
    if result.notes:
        print("Notes:", file=out)
        for note in result.notes:
            print(f"  • {note}", file=out)
    return 0
