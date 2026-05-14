"""CLI helpers for the `cronlens validate` and `cronlens lint` sub-commands."""

import sys
from argparse import ArgumentParser, Namespace
from typing import List

from cronlens.validator import validate
from cronlens.linter import lint


def _color(text: str, code: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"\033[{code}m{text}\033[0m"


def run_validate(args: Namespace) -> int:
    """Execute the validate sub-command. Returns exit code."""
    expression = " ".join(args.expression)
    result = validate(expression)
    use_color = not args.no_color

    if result.valid:
        status = _color("valid", "32", use_color)
        print(f"{expression!r} is {status}")
        return 0
    else:
        status = _color("invalid", "31", use_color)
        print(f"{expression!r} is {status}")
        for err in result.errors:
            print(f"  {_color('ERROR', '31', use_color)}: {err}")
        return 1


def run_lint(args: Namespace) -> int:
    """Execute the lint sub-command. Returns exit code (1 if invalid)."""
    expression = " ".join(args.expression)
    result = lint(expression)
    use_color = not args.no_color

    print(result.report())

    if result.has_warnings():
        warn_label = _color(f"{len(result.warnings)} warning(s)", "33", use_color)
        print(f"\n{warn_label} found.")

    return 0 if result.ok else 1


def build_validate_parser(subparsers) -> None:
    """Register validate + lint sub-commands on an existing subparsers action."""
    validate_p = subparsers.add_parser(
        "validate", help="Check whether a cron expression is syntactically valid"
    )
    validate_p.add_argument(
        "expression", nargs="+", help="Cron fields (5 tokens, quoted or space-separated)"
    )
    validate_p.add_argument("--no-color", action="store_true", help="Disable ANSI colour")
    validate_p.set_defaults(func=run_validate)

    lint_p = subparsers.add_parser(
        "lint", help="Validate and apply semantic checks to a cron expression"
    )
    lint_p.add_argument("expression", nargs="+", help="Cron expression fields")
    lint_p.add_argument("--no-color", action="store_true", help="Disable ANSI colour")
    lint_p.set_defaults(func=run_lint)
