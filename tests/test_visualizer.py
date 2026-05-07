"""Tests for cronlens.visualizer."""

from __future__ import annotations

from datetime import datetime

from cronlens.parser import CronExpression
from cronlens.visualizer import render_next_runs, _relative_label


_ANCHOR = datetime(2024, 3, 4, 10, 0, 0)


def test_render_contains_header():
    expr = CronExpression("* * * * *")
    output = render_next_runs(expr, n=3, now=_ANCHOR, color=False)
    assert "Datetime" in output
    assert "Relative" in output


def test_render_correct_row_count():
    expr = CronExpression("* * * * *")
    output = render_next_runs(expr, n=4, now=_ANCHOR, color=False)
    # rows are numbered 1..4
    for i in range(1, 5):
        assert str(i) in output


def test_render_no_color_has_no_ansi():
    expr = CronExpression("0 9 * * *")
    output = render_next_runs(expr, n=2, now=_ANCHOR, color=False)
    assert "\033[" not in output


def test_render_color_contains_ansi():
    expr = CronExpression("0 9 * * *")
    output = render_next_runs(expr, n=2, now=_ANCHOR, color=True)
    assert "\033[" in output


def test_relative_label_minutes():
    now = datetime(2024, 1, 1, 12, 0)
    future = datetime(2024, 1, 1, 12, 45)
    label = _relative_label(future, now)
    assert "minute" in label


def test_relative_label_hours():
    now = datetime(2024, 1, 1, 12, 0)
    future = datetime(2024, 1, 1, 15, 0)
    label = _relative_label(future, now)
    assert "hour" in label


def test_relative_label_days():
    now = datetime(2024, 1, 1, 12, 0)
    future = datetime(2024, 1, 3, 12, 0)
    label = _relative_label(future, now)
    assert "day" in label
