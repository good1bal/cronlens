"""Tests for cronlens.visualizer — covers both next-run and previous-run rendering."""

from datetime import datetime

import pytest

from cronlens.parser import CronExpression
from cronlens.visualizer import render_next_runs, render_prev_runs, _relative_label

REF = datetime(2024, 6, 15, 12, 30, 0)


# ---------------------------------------------------------------------------
# render_next_runs (existing behaviour, kept for regression)
# ---------------------------------------------------------------------------

def test_render_contains_header():
    expr = CronExpression("* * * * *")
    out = render_next_runs(expr, n=3, ref=REF, color=False)
    assert "Next 3 runs" in out


def test_render_correct_row_count():
    expr = CronExpression("* * * * *")
    out = render_next_runs(expr, n=4, ref=REF, color=False)
    lines = [l for l in out.splitlines() if l.strip() and "Next" not in l]
    assert len(lines) == 4


def test_render_no_color_has_no_ansi():
    expr = CronExpression("* * * * *")
    out = render_next_runs(expr, n=3, ref=REF, color=False)
    assert "\033[" not in out


def test_render_color_contains_ansi():
    expr = CronExpression("* * * * *")
    out = render_next_runs(expr, n=3, ref=REF, color=True)
    assert "\033[" in out


# ---------------------------------------------------------------------------
# render_prev_runs
# ---------------------------------------------------------------------------

def test_render_prev_contains_header():
    expr = CronExpression("* * * * *")
    out = render_prev_runs(expr, n=3, ref=REF, color=False)
    assert "Previous 3 runs" in out


def test_render_prev_correct_row_count():
    expr = CronExpression("* * * * *")
    out = render_prev_runs(expr, n=5, ref=REF, color=False)
    lines = [l for l in out.splitlines() if l.strip() and "Previous" not in l]
    assert len(lines) == 5


def test_render_prev_no_color_has_no_ansi():
    expr = CronExpression("* * * * *")
    out = render_prev_runs(expr, n=3, ref=REF, color=False)
    assert "\033[" not in out


def test_render_prev_color_contains_ansi():
    expr = CronExpression("* * * * *")
    out = render_prev_runs(expr, n=3, ref=REF, color=True)
    assert "\033[" in out


def test_render_prev_contains_ago():
    expr = CronExpression("* * * * *")
    out = render_prev_runs(expr, n=3, ref=REF, color=False)
    assert "ago" in out


# ---------------------------------------------------------------------------
# _relative_label
# ---------------------------------------------------------------------------

def test_relative_label_minutes():
    future = datetime(2024, 6, 15, 12, 45)
    label = _relative_label(future, REF)
    assert "minute" in label


def test_relative_label_hours():
    future = datetime(2024, 6, 15, 15, 30)
    label = _relative_label(future, REF)
    assert "hour" in label


def test_relative_label_days():
    future = datetime(2024, 6, 20, 12, 30)
    label = _relative_label(future, REF)
    assert "day" in label
