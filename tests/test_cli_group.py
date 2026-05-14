"""Tests for cronlens.cli_group."""

import argparse
import io
import sys
from unittest.mock import patch

import pytest

from cronlens.cli_group import build_group_parser, run_group


def _make_args(expressions, no_color=True):
    ns = argparse.Namespace()
    ns.expressions = expressions
    ns.no_color = no_color
    ns.func = run_group
    return ns


def test_build_group_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    build_group_parser(sub)
    args = root.parse_args(["group", "* * * * *"])
    assert hasattr(args, "func")


def test_run_group_exit_zero_for_valid_expressions(capsys):
    args = _make_args(["* * * * *", "0 9 * * *"])
    rc = run_group(args)
    assert rc == 0


def test_run_group_exit_one_when_invalid_present(capsys):
    args = _make_args(["* * * * *", "bad-expr"])
    rc = run_group(args)
    assert rc == 1


def test_run_group_output_contains_category(capsys):
    args = _make_args(["* * * * *"])
    run_group(args)
    out = capsys.readouterr().out
    assert "every-minute" in out


def test_run_group_output_contains_expression(capsys):
    args = _make_args(["0 9 * * *"])
    run_group(args)
    out = capsys.readouterr().out
    assert "0 9 * * *" in out


def test_run_group_invalid_shown_in_output(capsys):
    args = _make_args(["not-valid"])
    run_group(args)
    out = capsys.readouterr().out
    assert "invalid" in out
    assert "not-valid" in out


def test_run_group_no_color_no_ansi(capsys):
    args = _make_args(["* * * * *"], no_color=True)
    run_group(args)
    out = capsys.readouterr().out
    assert "\033[" not in out


def test_run_group_color_contains_ansi(capsys):
    args = _make_args(["* * * * *"], no_color=False)
    run_group(args)
    out = capsys.readouterr().out
    assert "\033[" in out


def test_run_group_multiple_categories_all_shown(capsys):
    args = _make_args(["* * * * *", "0 * * * *", "0 9 * * *"])
    run_group(args)
    out = capsys.readouterr().out
    assert "every-minute" in out
    assert "hourly" in out
    assert "daily" in out
