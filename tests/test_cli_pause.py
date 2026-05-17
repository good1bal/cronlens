"""Tests for cronlens.cli_pause."""

import argparse
import io
from datetime import datetime

import pytest

from cronlens.cli_pause import build_pause_parser, run_pause


def _make_args(
    expression: str = "0 * * * *",
    hours: int = 24,
    min_gap: int = 60,
    no_color: bool = True,
) -> argparse.Namespace:
    return argparse.Namespace(
        expression=expression,
        hours=hours,
        min_gap=min_gap,
        no_color=no_color,
    )


def test_build_pause_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    p = build_pause_parser(sub)
    assert p is not None


def test_build_pause_parser_has_expression_arg():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    build_pause_parser(sub)
    ns = root.parse_args(["pause", "* * * * *"])
    assert ns.expression == "* * * * *"


def test_build_pause_parser_default_hours():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    build_pause_parser(sub)
    ns = root.parse_args(["pause", "* * * * *"])
    assert ns.hours == 24


def test_build_pause_parser_default_min_gap():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    build_pause_parser(sub)
    ns = root.parse_args(["pause", "* * * * *"])
    assert ns.min_gap == 60


def test_run_pause_exit_zero_for_valid_expression():
    out = io.StringIO()
    code = run_pause(_make_args("0 * * * *"), out=out)
    assert code == 0


def test_run_pause_exit_one_for_invalid_expression():
    err = io.StringIO()
    code = run_pause(_make_args("not_valid"), err=err)
    assert code == 1


def test_run_pause_output_contains_header():
    out = io.StringIO()
    run_pause(_make_args("0 * * * *"), out=out)
    assert "Quiet windows for" in out.getvalue()


def test_run_pause_no_windows_message_when_every_minute():
    out = io.StringIO()
    run_pause(_make_args("* * * * *", min_gap=60), out=out)
    assert "No quiet windows" in out.getvalue()


def test_run_pause_hourly_reports_windows():
    out = io.StringIO()
    run_pause(_make_args("0 * * * *", hours=6, min_gap=30), out=out)
    assert "→" in out.getvalue()


def test_run_pause_total_quiet_time_in_output():
    out = io.StringIO()
    run_pause(_make_args("0 * * * *", hours=6, min_gap=30), out=out)
    assert "Total quiet time" in out.getvalue()


def test_run_pause_error_message_for_invalid_expression():
    err = io.StringIO()
    run_pause(_make_args("bad expr"), err=err)
    assert "Error" in err.getvalue()


def test_run_pause_no_color_no_ansi():
    out = io.StringIO()
    run_pause(_make_args("0 * * * *", no_color=True), out=out)
    assert "\033[" not in out.getvalue()
