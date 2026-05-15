"""Tests for cronlens.cli_heatmap."""

from __future__ import annotations

import argparse
import io
import sys

import pytest

from cronlens.cli_heatmap import build_heatmap_parser, run_heatmap


def _make_args(
    expression: str = "* * * * *",
    days: int = 1,
    no_color: bool = True,
) -> argparse.Namespace:
    return argparse.Namespace(expression=expression, days=days, no_color=no_color)


def test_build_heatmap_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    build_heatmap_parser(sub)
    args = root.parse_args(["heatmap", "* * * * *"])
    assert args.expression == "* * * * *"


def test_build_heatmap_parser_default_days():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    build_heatmap_parser(sub)
    args = root.parse_args(["heatmap", "0 * * * *"])
    assert args.days == 7


def test_run_heatmap_exit_zero_for_valid_expression(capsys):
    args = _make_args("0 * * * *", days=1)
    code = run_heatmap(args)
    assert code == 0


def test_run_heatmap_exit_one_for_invalid_expression(capsys):
    args = _make_args("not a cron", days=1)
    code = run_heatmap(args)
    assert code == 1


def test_run_heatmap_exit_one_for_zero_days(capsys):
    args = _make_args("* * * * *", days=0)
    code = run_heatmap(args)
    assert code == 1


def test_run_heatmap_output_contains_expression(capsys):
    args = _make_args("0 9 * * 1", days=1)
    run_heatmap(args)
    captured = capsys.readouterr()
    assert "0 9 * * 1" in captured.out


def test_run_heatmap_output_contains_day_labels(capsys):
    args = _make_args("* * * * *", days=1)
    run_heatmap(args)
    captured = capsys.readouterr()
    assert "Mon" in captured.out
    assert "Sun" in captured.out


def test_run_heatmap_output_contains_total(capsys):
    args = _make_args("0 * * * *", days=1)
    run_heatmap(args)
    captured = capsys.readouterr()
    assert "Total runs" in captured.out


def test_run_heatmap_error_goes_to_stderr(capsys):
    args = _make_args("bad expr", days=1)
    run_heatmap(args)
    captured = capsys.readouterr()
    assert "Invalid expression" in captured.err
    assert captured.out == ""


def test_run_heatmap_color_contains_ansi(capsys):
    args = _make_args("* * * * *", days=1, no_color=False)
    run_heatmap(args)
    captured = capsys.readouterr()
    assert "\033[" in captured.out
