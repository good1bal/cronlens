"""Tests for cronlens.cli_score."""

import argparse
import json
from io import StringIO

import pytest

from cronlens.cli_score import build_score_parser, run_score


def _make_args(expression: str, no_color: bool = True, as_json: bool = False) -> argparse.Namespace:
    return argparse.Namespace(expression=expression, no_color=no_color, json=as_json)


# ---------------------------------------------------------------------------
# build_score_parser
# ---------------------------------------------------------------------------

def test_build_score_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    subs = root.add_subparsers()
    p = build_score_parser(subs)
    assert p is not None


def test_build_score_parser_has_expression_arg():
    root = argparse.ArgumentParser()
    subs = root.add_subparsers()
    build_score_parser(subs)
    args = root.parse_args(["score", "* * * * *"])
    assert args.expression == "* * * * *"


# ---------------------------------------------------------------------------
# run_score — plain output
# ---------------------------------------------------------------------------

def test_run_score_exit_zero_for_valid_expression():
    out, err = StringIO(), StringIO()
    code = run_score(_make_args("* * * * *"), out=out, err=err)
    assert code == 0


def test_run_score_exit_one_for_invalid_expression():
    out, err = StringIO(), StringIO()
    code = run_score(_make_args("not a cron"), out=out, err=err)
    assert code == 1


def test_run_score_output_contains_complexity():
    out, err = StringIO(), StringIO()
    run_score(_make_args("* * * * *"), out=out, err=err)
    assert "Complexity" in out.getvalue()


def test_run_score_output_contains_predictability():
    out, err = StringIO(), StringIO()
    run_score(_make_args("* * * * *"), out=out, err=err)
    assert "Predictability" in out.getvalue()


def test_run_score_output_contains_expression():
    out, err = StringIO(), StringIO()
    run_score(_make_args("0 9 * * 1"), out=out, err=err)
    assert "0 9 * * 1" in out.getvalue()


def test_run_score_alias_resolved():
    out, err = StringIO(), StringIO()
    code = run_score(_make_args("@daily"), out=out, err=err)
    assert code == 0


def test_run_score_error_message_on_bad_expression():
    out, err = StringIO(), StringIO()
    run_score(_make_args("bad expr"), out=out, err=err)
    assert "error" in err.getvalue().lower()


# ---------------------------------------------------------------------------
# run_score — JSON output
# ---------------------------------------------------------------------------

def test_run_score_json_exit_zero():
    out, err = StringIO(), StringIO()
    code = run_score(_make_args("*/5 * * * *", as_json=True), out=out, err=err)
    assert code == 0


def test_run_score_json_is_valid_json():
    out, err = StringIO(), StringIO()
    run_score(_make_args("*/5 * * * *", as_json=True), out=out, err=err)
    data = json.loads(out.getvalue())
    assert isinstance(data, dict)


def test_run_score_json_has_required_keys():
    out, err = StringIO(), StringIO()
    run_score(_make_args("0 0 * * *", as_json=True), out=out, err=err)
    data = json.loads(out.getvalue())
    for key in ("expression", "complexity", "predictability", "notes"):
        assert key in data


def test_run_score_json_complexity_in_range():
    out, err = StringIO(), StringIO()
    run_score(_make_args("0 0 1 * *", as_json=True), out=out, err=err)
    data = json.loads(out.getvalue())
    assert 0 <= data["complexity"] <= 100


def test_run_score_json_notes_is_list():
    out, err = StringIO(), StringIO()
    run_score(_make_args("* * * * *", as_json=True), out=out, err=err)
    data = json.loads(out.getvalue())
    assert isinstance(data["notes"], list)
