"""CLI sub-command: annotate — show inline field annotations for a cron expression."""

from __future__ import annotations

import argparse
import sys
from typing import List

from cronlens.annotator import annotate
from cronlens.parser import CronParseError

_ANSI = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "cyan": "\033[36m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "green": "\033[32m",
}


def _color(text: str, *codes: str, use_color: bool = True) -> str:
    if not use_color:
        return text
    prefix = "".join(_ANSI[c] for c in codes)
    return f"{prefix}{text}{_ANSI['reset']}"


def build_annotate_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "annotate",
        help="Show inline field-level annotations for a cron expression",
    )
    p.add_argument("expression", nargs="+", help="Cron expression (5 fields)")
    p.add_argument("--no-color", action="store_true", help="Disable ANSI color output")
    return p


def run_annotate(args: argparse.Namespace) -> int:
    expression = " ".join(args.expression)
    use_color = not getattr(args, "no_color", False)

    try:
        result = annotate(expression)
    except CronParseError as exc:
        print(_color(f"Error: {exc}", "red", use_color=use_color), file=sys.stderr)
        return 1

    header = _color(f"# {result.expression}", "cyan", "bold", use_color=use_color)
    print(header)
    for field in result.fields:
        token_part = _color(f"{field.token:<12}", "yellow", use_color=use_color)
        label_part = _color(f"# {field.name}:", "bold", use_color=use_color)
        annotation_part = _color(field.annotation, "green", use_color=use_color)
        print(f"{token_part}{label_part} {annotation_part}")
    return 0
