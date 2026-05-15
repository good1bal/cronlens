"""Tests for cronlens.cli_profile."""

import argparse
import json

import pytest

from cronlens.cli_profile import build_profile_parser, run_profile


def _make_args(expression: str, hours: int = 24, no_color: bool = True) -> argparse.Namespace:
    return argparse.Namespace(expression=expression, hours=hours, no_color=no_color)


# ---------------------------------------------------------------------------
# Parser registration
# ---------------------------------------------------------------------------

def test_build_profile_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    build_profile_parser(sub)
    args = root.parse_args(["profile", "* * * * *"])
    assert hasattr(args, "expression")


def test_build_profile_parser_has_hours_arg():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    build_profile_parser(sub)
    args = root.parse_args(["profile", "0 * * * *", "--hours", "12"])
    assert args.hours == 12


def test_build_profile_parser_default_hours():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    build_profile_parser(sub)
    args = root.parse_args(["profile", "* * * * *"])
    assert args.hours == 24


# ---------------------------------------------------------------------------
# run_profile exit codes
# ---------------------------------------------------------------------------

def test_run_profile_exit_zero_for_valid_expression():
    args = _make_args("* * * * *")
    assert run_profile(args) == 0


def test_run_profile_exit_one_for_invalid_expression():
    args = _make_args("not_a_cron")
    assert run_profile(args) == 1


def test_run_profile_exit_zero_for_alias():
    args = _make_args("@daily")
    assert run_profile(args) == 0


# ---------------------------------------------------------------------------
# run_profile output
# ---------------------------------------------------------------------------

def test_run_profile_output_contains_window(capsys):
    args = _make_args("* * * * *", hours=6)
    run_profile(args)
    captured = capsys.readouterr()
    assert "6h" in captured.out


def test_run_profile_output_contains_total_runs(capsys):
    args = _make_args("0 9 * * *", hours=24)
    run_profile(args)
    captured = capsys.readouterr()
    assert "Total runs" in captured.out


def test_run_profile_output_has_24_hour_rows(capsys):
    args = _make_args("* * * * *", hours=24)
    run_profile(args)
    captured = capsys.readouterr()
    # Each hour row starts with HH:00
    rows = [l for l in captured.out.splitlines() if ":00" in l]
    assert len(rows) == 24


def test_run_profile_no_color_no_ansi(capsys):
    args = _make_args("* * * * *", no_color=True)
    run_profile(args)
    captured = capsys.readouterr()
    assert "\033[" not in captured.out


def test_run_profile_error_to_stderr(capsys):
    args = _make_args("bad expression")
    run_profile(args)
    captured = capsys.readouterr()
    assert "Error" in captured.err
