"""CLI sub-command: compare two cron expressions field-by-field."""

from __future__ import annotations

import argparse
import sys
from typing import List

from cronlens.differ import CronDiff
from cronlens.parser import CronExpression, CronParseError

# ANSI colour helpers (same pattern used across other cli_*.py modules)
_RESET = "\033[0m"
_BOLD = "\033[1m"
_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"


def _color(text: str, code: str, *, use_color: bool) -> str:
    """Wrap *text* in an ANSI escape *code* when color is enabled."""
    if not use_color:
        return text
    return f"{code}{text}{_RESET}"


def build_diff_parser(subparsers: "argparse._SubParsersAction") -> argparse.ArgumentParser:  # type: ignore[type-arg]
    """Register the *diff* sub-command and return its parser."""
    p = subparsers.add_parser(
        "diff",
        help="Compare two cron expressions and show field-level differences.",
        description=(
            "Parse two cron expressions and display a side-by-side diff of "
            "every field, highlighting which fields differ."
        ),
    )
    p.add_argument("expr_a", metavar="EXPR_A", help="First cron expression.")
    p.add_argument("expr_b", metavar="EXPR_B", help="Second cron expression.")
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI colour output.",
    )
    return p


def run_diff(args: argparse.Namespace, out=sys.stdout, err=sys.stderr) -> int:
    """Execute the *diff* sub-command.

    Returns 0 when the two expressions are identical, 1 when they differ,
    and 2 on a parse error.
    """
    use_color = not args.no_color

    # --- parse both expressions -------------------------------------------
    try:
        expr_a = CronExpression(args.expr_a)
    except CronParseError as exc:
        print(
            _color("Error", _RED, use_color=use_color)
            + f" parsing EXPR_A: {exc}",
            file=err,
        )
        return 2

    try:
        expr_b = CronExpression(args.expr_b)
    except CronParseError as exc:
        print(
            _color("Error", _RED, use_color=use_color)
            + f" parsing EXPR_B: {exc}",
            file=err,
        )
        return 2

    diff = CronDiff(expr_a, expr_b)

    # --- header -----------------------------------------------------------
    header = _color("cronlens diff", _BOLD, use_color=use_color)
    print(f"{header}\n", file=out)
    print(
        f"  {_color('A', _CYAN, use_color=use_color)}: {args.expr_a}",
        file=out,
    )
    print(
        f"  {_color('B', _CYAN, use_color=use_color)}: {args.expr_b}",
        file=out,
    )
    print(file=out)

    # --- field table ------------------------------------------------------
    field_names = ["minute", "hour", "day", "month", "weekday"]
    values_a: List[str] = [
        expr_a.minute_raw,
        expr_a.hour_raw,
        expr_a.day_raw,
        expr_a.month_raw,
        expr_a.weekday_raw,
    ]
    values_b: List[str] = [
        expr_b.minute_raw,
        expr_b.hour_raw,
        expr_b.day_raw,
        expr_b.month_raw,
        expr_b.weekday_raw,
    ]

    col_w = max(len(n) for n in field_names) + 2
    val_w = max(max(len(v) for v in values_a), max(len(v) for v in values_b), 8) + 2

    header_row = (
        _color("Field".ljust(col_w), _BOLD, use_color=use_color)
        + _color("A".ljust(val_w), _BOLD, use_color=use_color)
        + _color("B".ljust(val_w), _BOLD, use_color=use_color)
        + _color("Status", _BOLD, use_color=use_color)
    )
    print(header_row, file=out)
    print("-" * (col_w + val_w * 2 + 8), file=out)

    for name, va, vb, fd in zip(field_names, values_a, values_b, diff.fields):
        if fd is None:
            # identical field
            status = _color("same", _GREEN, use_color=use_color)
            row = name.ljust(col_w) + va.ljust(val_w) + vb.ljust(val_w) + status
        else:
            status = _color("CHANGED", _YELLOW, use_color=use_color)
            row = (
                _color(name.ljust(col_w), _RED, use_color=use_color)
                + _color(va.ljust(val_w), _RED, use_color=use_color)
                + _color(vb.ljust(val_w), _YELLOW, use_color=use_color)
                + status
            )
        print(row, file=out)

    # --- summary ----------------------------------------------------------
    print(file=out)
    print(diff.summary(), file=out)

    return 0 if diff.is_identical() else 1
