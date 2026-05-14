"""Tests for cronlens.exporter."""

from __future__ import annotations

import json
from datetime import datetime

import pytest

from cronlens.parser import CronExpression
from cronlens.exporter import export_json, export_text

REF = datetime(2024, 6, 15, 12, 0)


@pytest.fixture
def every_minute() -> CronExpression:
    return CronExpression("* * * * *")


@pytest.fixture
def specific() -> CronExpression:
    return CronExpression("30 9 * * 1")


def test_export_json_is_valid_json(every_minute):
    raw = export_json(every_minute, ref=REF)
    data = json.loads(raw)  # must not raise
    assert isinstance(data, dict)


def test_export_json_contains_expression(every_minute):
    data = json.loads(export_json(every_minute, ref=REF))
    assert data["expression"] == "* * * * *"


def test_export_json_next_runs_count(every_minute):
    data = json.loads(export_json(every_minute, ref=REF, next_n=3))
    assert len(data["next_runs"]) == 3


def test_export_json_prev_runs_count(every_minute):
    data = json.loads(export_json(every_minute, ref=REF, prev_n=4))
    assert len(data["prev_runs"]) == 4


def test_export_json_next_runs_after_ref(every_minute):
    data = json.loads(export_json(every_minute, ref=REF, next_n=5))
    ref_iso = REF.isoformat(timespec="seconds")
    for run in data["next_runs"]:
        assert run > ref_iso


def test_export_json_prev_runs_before_ref(every_minute):
    data = json.loads(export_json(every_minute, ref=REF, prev_n=5))
    ref_iso = REF.isoformat(timespec="seconds")
    for run in data["prev_runs"]:
        assert run < ref_iso


def test_export_json_fields_present(specific):
    data = json.loads(export_json(specific, ref=REF))
    assert set(data["fields"].keys()) == {"minute", "hour", "day", "month", "weekday"}


def test_export_json_explanation_nonempty(specific):
    data = json.loads(export_json(specific, ref=REF))
    assert data["explanation"] and isinstance(data["explanation"], str)


def test_export_text_contains_expression(every_minute):
    out = export_text(every_minute, ref=REF)
    assert "* * * * *" in out


def test_export_text_contains_next_section(every_minute):
    out = export_text(every_minute, ref=REF)
    assert "Next runs:" in out


def test_export_text_contains_prev_section(every_minute):
    out = export_text(every_minute, ref=REF)
    assert "Previous runs:" in out


def test_export_text_next_count(every_minute):
    out = export_text(every_minute, ref=REF, next_n=2)
    lines_after = out.split("Next runs:")[1].split("Previous runs:")[0]
    entries = [l for l in lines_after.splitlines() if l.strip()]
    assert len(entries) == 2
