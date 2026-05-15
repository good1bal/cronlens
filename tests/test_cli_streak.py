"""Tests for cronlens.cli_streak."""

from __future__ import annotations

import argparse

import pytest

from cronlens.cli_streak import build_streak_parser, run_streak


def _make_args(
    expression: str = "* * * * *",
    days: int = 7,
    no_color: bool = True,
) -> argparse.Namespace:
    return argparse.Namespace(expression=expression, days=days, no_color=no_color)


def test_build_streak_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    build_streak_parser(sub)
    args = root.parse_args(["streak", "* * * * *"])
    assert args.expression == "* * * * *"


def test_build_streak_parser_default_days():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    build_streak_parser(sub)
    args = root.parse_args(["streak", "* * * * *"])
    assert args.days == 30


def test_run_streak_exit_zero_for_valid_expression():
    assert run_streak(_make_args("* * * * *", days=2)) == 0


def test_run_streak_exit_one_for_invalid_expression():
    assert run_streak(_make_args("not_a_cron")) == 1


def test_run_streak_exit_one_for_zero_days():
    assert run_streak(_make_args("* * * * *", days=0)) == 1


def test_run_streak_output_contains_expression(capsys):
    run_streak(_make_args("*/5 * * * *", days=2))
    out = capsys.readouterr().out
    assert "*/5 * * * *" in out


def test_run_streak_output_contains_window(capsys):
    run_streak(_make_args("* * * * *", days=5))
    out = capsys.readouterr().out
    assert "5" in out


def test_run_streak_output_contains_longest_day_streak(capsys):
    run_streak(_make_args("* * * * *", days=3))
    out = capsys.readouterr().out
    assert "day streak" in out.lower() or "day" in out.lower()


def test_run_streak_output_contains_longest_hour_streak(capsys):
    run_streak(_make_args("* * * * *", days=1))
    out = capsys.readouterr().out
    assert "hour streak" in out.lower() or "hour" in out.lower()


def test_run_streak_no_color_no_ansi(capsys):
    run_streak(_make_args("* * * * *", days=1, no_color=True))
    out = capsys.readouterr().out
    assert "\033[" not in out
