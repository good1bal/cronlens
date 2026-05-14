"""Tests for cronlens.cli_annotate."""

import argparse
import sys
from io import StringIO

import pytest

from cronlens.cli_annotate import build_annotate_parser, run_annotate


def _make_args(expression: str, no_color: bool = True) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(dest="command")
    build_annotate_parser(subs)
    parts = ["annotate"] + expression.split()
    if no_color:
        parts.append("--no-color")
    return parser.parse_args(parts)


# ---------------------------------------------------------------------------
# parser registration
# ---------------------------------------------------------------------------

def test_build_annotate_parser_registers_subcommand():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(dest="command")
    build_annotate_parser(subs)
    args = parser.parse_args(["annotate", "*", "*", "*", "*", "*"])
    assert args.command == "annotate"


def test_build_annotate_parser_has_expression_arg():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(dest="command")
    build_annotate_parser(subs)
    args = parser.parse_args(["annotate", "0", "9", "*", "*", "1"])
    assert args.expression == ["0", "9", "*", "*", "1"]


# ---------------------------------------------------------------------------
# run_annotate exit codes
# ---------------------------------------------------------------------------

def test_run_annotate_exit_zero_for_valid_expression():
    args = _make_args("* * * * *")
    assert run_annotate(args) == 0


def test_run_annotate_exit_one_for_invalid_expression(capsys):
    args = _make_args("not a cron expression here")
    # override to make it clearly invalid (6 tokens but nonsense values)
    args.expression = ["99", "99", "*", "*", "*"]
    rc = run_annotate(args)
    assert rc == 1


# ---------------------------------------------------------------------------
# run_annotate output content
# ---------------------------------------------------------------------------

def test_run_annotate_output_contains_expression(capsys):
    args = _make_args("0 9 * * 1")
    run_annotate(args)
    out = capsys.readouterr().out
    assert "0 9 * * 1" in out


def test_run_annotate_output_contains_field_names(capsys):
    args = _make_args("0 9 * * 1")
    run_annotate(args)
    out = capsys.readouterr().out
    for name in ["minute", "hour", "day", "month", "weekday"]:
        assert name in out


def test_run_annotate_output_has_six_lines(capsys):
    args = _make_args("* * * * *")
    run_annotate(args)
    out = capsys.readouterr().out
    lines = [l for l in out.splitlines() if l.strip()]
    assert len(lines) == 6


def test_run_annotate_no_color_no_ansi(capsys):
    args = _make_args("*/15 * * * *", no_color=True)
    run_annotate(args)
    out = capsys.readouterr().out
    assert "\033[" not in out


def test_run_annotate_error_written_to_stderr(capsys):
    args = _make_args("* * *")  # too few fields
    args.expression = ["*", "*", "*"]  # force invalid
    run_annotate(args)
    err = capsys.readouterr().err
    assert len(err) > 0
