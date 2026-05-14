"""Tests for cronlens.cli_classify."""

import io
import argparse
import pytest

from cronlens.cli_classify import build_classify_parser, run_classify


def _make_args(expression: str, no_color: bool = True) -> argparse.Namespace:
    ns = argparse.Namespace()
    ns.expression = expression
    ns.no_color = no_color
    return ns


def test_build_classify_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    p = build_classify_parser(sub)
    assert p is not None


def test_run_classify_exit_zero_for_valid_expression():
    out = io.StringIO()
    code = run_classify(_make_args("* * * * *"), output=out)
    assert code == 0


def test_run_classify_exit_one_for_invalid_expression():
    code = run_classify(_make_args("not-a-cron"))
    assert code == 1


def test_run_classify_output_contains_category():
    out = io.StringIO()
    run_classify(_make_args("* * * * *"), output=out)
    assert "EVERY-MINUTE" in out.getvalue()


def test_run_classify_output_contains_expression():
    out = io.StringIO()
    run_classify(_make_args("0 9 * * *"), output=out)
    assert "0 9 * * *" in out.getvalue()


def test_run_classify_daily():
    out = io.StringIO()
    run_classify(_make_args("0 9 * * *"), output=out)
    assert "DAILY" in out.getvalue()


def test_run_classify_weekly():
    out = io.StringIO()
    run_classify(_make_args("0 8 * * 1"), output=out)
    assert "WEEKLY" in out.getvalue()


def test_run_classify_alias_at_daily():
    out = io.StringIO()
    code = run_classify(_make_args("@daily"), output=out)
    assert code == 0
    assert "DAILY" in out.getvalue()


def test_run_classify_no_color_no_ansi():
    out = io.StringIO()
    run_classify(_make_args("* * * * *", no_color=True), output=out)
    assert "\033[" not in out.getvalue()
