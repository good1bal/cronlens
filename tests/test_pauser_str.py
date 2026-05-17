"""Tests for string representations in cronlens.pauser."""

from datetime import datetime

from cronlens.pauser import QuietWindow, PauseResult


def _window(start_hour: int, end_hour: int) -> QuietWindow:
    return QuietWindow(
        start=datetime(2024, 1, 15, start_hour, 0),
        end=datetime(2024, 1, 15, end_hour, 0),
    )


def test_quiet_window_str_contains_arrow():
    w = _window(6, 8)
    assert "→" in str(w)


def test_quiet_window_str_contains_start_time():
    w = _window(6, 8)
    assert "06:00" in str(w)


def test_quiet_window_str_contains_end_time():
    w = _window(6, 8)
    assert "08:00" in str(w)


def test_quiet_window_str_contains_duration():
    w = _window(6, 8)
    assert "120" in str(w)


def test_pause_result_str_contains_expression_label():
    r = PauseResult(expression="0 * * * *", window_hours=24)
    assert "Expression" in str(r)


def test_pause_result_str_contains_window_label():
    r = PauseResult(expression="0 * * * *", window_hours=24)
    assert "Window" in str(r)


def test_pause_result_str_contains_quiet_gaps_label():
    r = PauseResult(expression="0 * * * *", window_hours=24)
    assert "Quiet gaps" in str(r)


def test_pause_result_str_contains_total_quiet_label():
    r = PauseResult(expression="0 * * * *", window_hours=24)
    assert "Total quiet" in str(r)


def test_pause_result_str_contains_longest_when_windows_present():
    r = PauseResult(expression="0 * * * *", window_hours=24)
    r.windows = [_window(1, 3), _window(5, 9)]
    assert "Longest gap" in str(r)


def test_pause_result_str_no_longest_when_empty():
    r = PauseResult(expression="0 * * * *", window_hours=24)
    assert "Longest gap" not in str(r)


def test_pause_result_str_lists_all_windows():
    r = PauseResult(expression="0 * * * *", window_hours=24)
    r.windows = [_window(1, 3), _window(5, 9), _window(10, 14)]
    text = str(r)
    assert text.count("→") == 3
