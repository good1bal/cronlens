"""Tests for cronlens.cli_calendar."""

from __future__ import annotations

import argparse
import io

import pytest

from cronlens.cli_calendar import build_calendar_parser, run_calendar


def _make_args(expression: str, weeks: int = 1, no_color: bool = True) -> argparse.Namespace:
    return argparse.Namespace(expression=expression, weeks=weeks, no_color=no_color)


def test_build_calendar_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    build_calendar_parser(sub)
    args = root.parse_args(["calendar", "* * * * *"])
    assert args.expression == "* * * * *"


def test_build_calendar_parser_default_weeks():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    build_calendar_parser(sub)
    args = root.parse_args(["calendar", "* * * * *"])
    assert args.weeks == 1


def test_run_calendar_exit_zero_for_valid_expression():
    args = _make_args("* * * * *")
    out = io.StringIO()
    rc = run_calendar(args, out=out)
    assert rc == 0


def test_run_calendar_exit_one_for_invalid_expression():
    args = _make_args("not a cron")
    err = io.StringIO()
    rc = run_calendar(args, err=err)
    assert rc == 1


def test_run_calendar_exit_one_for_zero_weeks():
    args = _make_args("* * * * *", weeks=0)
    err = io.StringIO()
    rc = run_calendar(args, err=err)
    assert rc == 1


def test_run_calendar_output_contains_day_names():
    from cronlens.calendar_view import DAY_NAMES
    args = _make_args("0 9 * * *")
    out = io.StringIO()
    run_calendar(args, out=out)
    text = out.getvalue()
    for name in DAY_NAMES:
        assert name in text


def test_run_calendar_output_contains_expression():
    args = _make_args("0 9 * * 1")
    out = io.StringIO()
    run_calendar(args, out=out)
    assert "0 9 * * 1" in out.getvalue()


def test_run_calendar_output_contains_total():
    args = _make_args("0 12 * * *")
    out = io.StringIO()
    run_calendar(args, out=out)
    assert "Total fires" in out.getvalue()


def test_run_calendar_color_contains_ansi():
    args = _make_args("* * * * *", no_color=False)
    out = io.StringIO()
    run_calendar(args, out=out)
    assert "\033[" in out.getvalue()


def test_run_calendar_no_color_has_no_ansi():
    args = _make_args("* * * * *", no_color=True)
    out = io.StringIO()
    run_calendar(args, out=out)
    assert "\033[" not in out.getvalue()
