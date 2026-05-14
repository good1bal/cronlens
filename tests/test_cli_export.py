"""Tests for cronlens.cli_export."""

from __future__ import annotations

import argparse
import json
from unittest.mock import patch

import pytest

from cronlens.cli_export import build_export_parser, run_export


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "expression": "* * * * *",
        "fmt": "json",
        "next_n": 5,
        "prev_n": 5,
        "ref": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_run_export_json_exit_zero(capsys):
    rc = run_export(_make_args())
    assert rc == 0


def test_run_export_json_valid_json(capsys):
    run_export(_make_args())
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "expression" in data


def test_run_export_text_exit_zero(capsys):
    rc = run_export(_make_args(fmt="text"))
    assert rc == 0


def test_run_export_text_output(capsys):
    run_export(_make_args(fmt="text"))
    out = capsys.readouterr().out
    assert "Expression" in out


def test_run_export_invalid_expression(capsys):
    rc = run_export(_make_args(expression="not valid at all"))
    assert rc == 1
    assert "Parse error" in capsys.readouterr().err


def test_run_export_invalid_ref(capsys):
    rc = run_export(_make_args(ref="not-a-date"))
    assert rc == 1
    assert "Invalid --ref" in capsys.readouterr().err


def test_run_export_valid_ref(capsys):
    rc = run_export(_make_args(ref="2024-01-01T08:00:00"))
    assert rc == 0


def test_build_export_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    build_export_parser(sub)
    args = root.parse_args(["export", "* * * * *", "--format", "text", "--next", "3"])
    assert args.next_n == 3
    assert args.fmt == "text"
