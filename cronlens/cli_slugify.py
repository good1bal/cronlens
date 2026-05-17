"""CLI sub-command: cronlens slugify <expression>"""

from __future__ import annotations

import argparse
import sys

from cronlens.parser import CronParseError
from cronlens.slugifier import slugify


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def build_slugify_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "slugify",
        help="Convert a cron expression to a human-friendly slug",
    )
    p.add_argument("expression", help="Cron expression, e.g. '*/5 * * * *'")
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI colour output",
    )
    p.add_argument(
        "--slug-only",
        action="store_true",
        default=False,
        help="Print only the slug string",
    )
    return p


def run_slugify(args: argparse.Namespace, out=sys.stdout, err=sys.stderr) -> int:
    try:
        result = slugify(args.expression)
    except CronParseError as exc:
        msg = f"Error: {exc}\n"
        err.write(_color(msg, "31") if not args.no_color else msg)
        return 1

    if args.slug_only:
        out.write(result.slug + "\n")
        return 0

    if args.no_color:
        out.write(str(result) + "\n")
    else:
        out.write(
            _color("Expression : ", "90") + result.expression + "\n"
            + _color("Slug       : ", "90") + _color(result.slug, "36") + "\n"
            + _color("Tokens     : ", "90") + " | ".join(result.tokens) + "\n"
        )
    return 0
