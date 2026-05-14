"""CLI sub-command: classify — show the schedule category of a cron expression."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from cronlens.parser import CronExpression, CronParseError
from cronlens.classifier import classify
from cronlens.aliaser import is_alias, resolve

_ANSI = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "cyan": "\033[36m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "red": "\033[31m",
}

_CATEGORY_COLORS = {
    "every-minute": "yellow",
    "hourly": "cyan",
    "daily": "green",
    "weekly": "green",
    "monthly": "cyan",
    "yearly": "cyan",
    "custom": "yellow",
}


def _color(text: str, name: str, use_color: bool) -> str:
    if not use_color:
        return text
    code = _ANSI.get(name, "")
    return f"{code}{text}{_ANSI['reset']}"


def build_classify_parser(subparsers) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "classify",
        help="Classify a cron expression into a schedule category",
    )
    p.add_argument("expression", help="Cron expression or @alias")
    p.add_argument("--no-color", action="store_true", help="Disable ANSI color output")
    return p


def run_classify(args: argparse.Namespace, output=sys.stdout) -> int:
    raw: str = args.expression
    use_color: bool = not getattr(args, "no_color", False)

    try:
        if is_alias(raw):
            raw = resolve(raw)
        expr = CronExpression(raw)
    except Exception as exc:  # CronParseError or AliasError
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    result = classify(expr)
    cat_color = _CATEGORY_COLORS.get(result.category, "reset")

    expr_str = _color(result.expression, "bold", use_color)
    cat_str = _color(result.category.upper(), cat_color, use_color)
    desc_str = result.description

    print(f"Expression : {expr_str}", file=output)
    print(f"Category   : {cat_str}", file=output)
    print(f"Description: {desc_str}", file=output)
    return 0
