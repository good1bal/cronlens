"""Tests for cronlens.cli_template."""

import argparse
import sys
from io import StringIO
from unittest.mock import patch

import pytest

from cronlens.cli_template import build_template_parser, run_template


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "template_cmd": "list",
        "search": None,
        "name": "daily",
        "next": 5,
        "no_color": True,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


# ---------------------------------------------------------------------------
# build_template_parser
# ---------------------------------------------------------------------------

def test_build_template_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="cmd")
    build_template_parser(sub)
    args = root.parse_args(["template", "list"])
    assert args.cmd == "template"


# ---------------------------------------------------------------------------
# run_template – list
# ---------------------------------------------------------------------------

def test_run_list_exit_zero(capsys):
    args = _make_args(template_cmd="list", search=None)
    rc = run_template(args)
    assert rc == 0


def test_run_list_output_contains_daily(capsys):
    args = _make_args(template_cmd="list", search=None)
    run_template(args)
    out = capsys.readouterr().out
    assert "daily" in out


def test_run_list_output_contains_expression(capsys):
    args = _make_args(template_cmd="list", search=None)
    run_template(args)
    out = capsys.readouterr().out
    assert "* * * * *" in out


def test_run_list_search_filters(capsys):
    args = _make_args(template_cmd="list", search="hourly")
    rc = run_template(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "hourly" in out


def test_run_list_search_no_match_returns_one(capsys):
    args = _make_args(template_cmd="list", search="zzznomatch")
    rc = run_template(args)
    assert rc == 1


# ---------------------------------------------------------------------------
# run_template – show
# ---------------------------------------------------------------------------

def test_run_show_exit_zero(capsys):
    args = _make_args(template_cmd="show", name="daily", next=3, no_color=True)
    rc = run_template(args)
    assert rc == 0


def test_run_show_contains_template_name(capsys):
    args = _make_args(template_cmd="show", name="weekly", next=2, no_color=True)
    run_template(args)
    out = capsys.readouterr().out
    assert "weekly" in out


def test_run_show_contains_expression(capsys):
    args = _make_args(template_cmd="show", name="hourly", next=2, no_color=True)
    run_template(args)
    out = capsys.readouterr().out
    assert "0 * * * *" in out


def test_run_show_unknown_template_returns_one(capsys):
    args = _make_args(template_cmd="show", name="no-such-template", next=3, no_color=True)
    rc = run_template(args)
    assert rc == 1


def test_run_show_unknown_template_stderr(capsys):
    args = _make_args(template_cmd="show", name="no-such-template", next=3, no_color=True)
    run_template(args)
    err = capsys.readouterr().err
    assert "Unknown template" in err
