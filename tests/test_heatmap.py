"""Tests for cronlens.heatmap."""

from __future__ import annotations

from datetime import datetime

import pytest

from cronlens.parser import CronExpression
from cronlens.heatmap import HeatmapResult, build_heatmap, DAYS, HOURS


def _expr(s: str) -> CronExpression:
    return CronExpression(s)


def test_build_heatmap_returns_heatmap_result():
    result = build_heatmap(_expr("* * * * *"), window_days=1)
    assert isinstance(result, HeatmapResult)


def test_heatmap_stores_expression():
    result = build_heatmap(_expr("0 * * * *"), window_days=1)
    assert result.expression == "0 * * * *"


def test_heatmap_stores_window_days():
    result = build_heatmap(_expr("* * * * *"), window_days=3)
    assert result.window_days == 3


def test_grid_shape():
    result = build_heatmap(_expr("* * * * *"), window_days=1)
    assert len(result.grid) == 7
    assert all(len(row) == 24 for row in result.grid)


def test_every_minute_total_runs_one_day():
    result = build_heatmap(_expr("* * * * *"), window_days=1)
    # 1 day = 1440 minutes
    assert result.total() == 1440


def test_hourly_total_runs_one_week():
    result = build_heatmap(_expr("0 * * * *"), window_days=7)
    # 7 days * 24 hours = 168
    assert result.total() == 168


def test_peak_is_max_cell():
    result = build_heatmap(_expr("* * * * *"), window_days=1)
    flat = [v for row in result.grid for v in row]
    assert result.peak() == max(flat)


def test_window_days_less_than_one_raises():
    with pytest.raises(ValueError):
        build_heatmap(_expr("* * * * *"), window_days=0)


def test_str_contains_expression():
    result = build_heatmap(_expr("0 9 * * 1"), window_days=7)
    assert "0 9 * * 1" in str(result)


def test_str_contains_day_labels():
    result = build_heatmap(_expr("* * * * *"), window_days=1)
    text = str(result)
    for day in DAYS:
        assert day in text


def test_str_contains_total_runs():
    result = build_heatmap(_expr("0 * * * *"), window_days=1)
    text = str(result)
    assert "Total runs" in text
    assert str(result.total()) in text


def test_str_contains_window_info():
    result = build_heatmap(_expr("* * * * *"), window_days=4)
    assert "4d" in str(result)
