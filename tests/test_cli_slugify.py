"""Tests for cronlens.cli_slugify."""

import argparse
import io

from cronlens.cli_slugify import build_slugify_parser, run_slugify


def _make_args(expression: str, no_color: bool = True, slug_only: bool = False) -> argparse.Namespace:
    return argparse.Namespace(
        expression=expression,
        no_color=no_color,
        slug_only=slug_only,
    )


def test_build_slugify_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    p = build_slugify_parser(sub)
    assert p is not None


def test_run_slugify_exit_zero_for_valid_expression():
    args = _make_args("* * * * *")
    assert run_slugify(args, out=io.StringIO(), err=io.StringIO()) == 0


def test_run_slugify_exit_one_for_invalid_expression():
    args = _make_args("bad expression here")
    assert run_slugify(args, out=io.StringIO(), err=io.StringIO()) == 1


def test_run_slugify_output_contains_slug_label():
    out = io.StringIO()
    run_slugify(_make_args("0 9 * * 1"), out=out, err=io.StringIO())
    assert "Slug" in out.getvalue()


def test_run_slugify_output_contains_expression():
    out = io.StringIO()
    run_slugify(_make_args("0 9 * * 1"), out=out, err=io.StringIO())
    assert "0 9 * * 1" in out.getvalue()


def test_run_slugify_slug_only_flag():
    out = io.StringIO()
    args = _make_args("*/5 * * * *", slug_only=True)
    code = run_slugify(args, out=out, err=io.StringIO())
    assert code == 0
    lines = out.getvalue().strip().splitlines()
    assert len(lines) == 1  # only the slug, nothing else


def test_run_slugify_slug_only_no_labels():
    out = io.StringIO()
    args = _make_args("0 0 * * *", slug_only=True)
    run_slugify(args, out=out, err=io.StringIO())
    assert "Expression" not in out.getvalue()
    assert "Tokens" not in out.getvalue()


def test_run_slugify_error_written_to_stderr():
    err = io.StringIO()
    run_slugify(_make_args("garbage"), out=io.StringIO(), err=err)
    assert "Error" in err.getvalue()


def test_run_slugify_color_output_contains_ansi():
    out = io.StringIO()
    args = _make_args("* * * * *", no_color=False)
    run_slugify(args, out=out, err=io.StringIO())
    assert "\033[" in out.getvalue()


def test_run_slugify_no_color_output_has_no_ansi():
    out = io.StringIO()
    args = _make_args("* * * * *", no_color=True)
    run_slugify(args, out=out, err=io.StringIO())
    assert "\033[" not in out.getvalue()
