"""CLI sub-commands for template listing and lookup."""

from __future__ import annotations

import argparse
import sys
from typing import List

from cronlens.templater import TemplateError, all_templates, get, search
from cronlens.next_run import next_runs
from cronlens.visualizer import render_next_runs


def build_template_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "template",
        help="List or look up named cron templates",
    )
    sub = p.add_subparsers(dest="template_cmd", required=True)

    # list
    list_p = sub.add_parser("list", help="Print all available templates")
    list_p.add_argument(
        "--search", metavar="KEYWORD",
        help="Filter templates by keyword",
    )

    # show
    show_p = sub.add_parser("show", help="Show details for a named template")
    show_p.add_argument("name", help="Template name (e.g. 'daily')")
    show_p.add_argument(
        "--next", metavar="N", type=int, default=5,
        help="Number of upcoming runs to display (default: 5)",
    )
    show_p.add_argument(
        "--no-color", action="store_true",
        help="Disable ANSI colour output",
    )


def run_template(args: argparse.Namespace) -> int:
    if args.template_cmd == "list":
        return _run_list(args)
    if args.template_cmd == "show":
        return _run_show(args)
    return 1


def _run_list(args: argparse.Namespace) -> int:
    keyword = getattr(args, "search", None)
    templates = search(keyword) if keyword else all_templates()
    if not templates:
        print(f"No templates matching {keyword!r}.", file=sys.stderr)
        return 1
    col_w = max(len(t.name) for t in templates)
    print(f"{'NAME':<{col_w}}  {'EXPRESSION':<17}  DESCRIPTION")
    print("-" * 72)
    for t in templates:
        print(f"{t.name:<{col_w}}  {t.expression:<17}  {t.description}")
    return 0


def _run_show(args: argparse.Namespace) -> int:
    try:
        t = get(args.name)
    except TemplateError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    color = not getattr(args, "no_color", False)
    expr = t.to_cron()
    runs = next_runs(expr, n=args.next)
    print(f"Template : {t.name}")
    print(f"Expression: {t.expression}")
    print(f"Description: {t.description}")
    print()
    print(render_next_runs(runs, color=color))
    return 0
