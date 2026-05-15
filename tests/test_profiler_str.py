"""Tests for ProfileResult.__str__."""

from cronlens.profiler import ProfileResult


def _make_result(**kwargs) -> ProfileResult:
    defaults = dict(
        expression="* * * * *",
        window_hours=24,
        total_runs=1440,
        runs_per_hour={h: 60 for h in range(24)},
        busiest_hour=0,
        quietest_hour=0,
    )
    defaults.update(kwargs)
    return ProfileResult(**defaults)


def test_str_contains_expression():
    r = _make_result(expression="0 9 * * *")
    assert "0 9 * * *" in str(r)


def test_str_contains_window_hours():
    r = _make_result(window_hours=12)
    assert "12" in str(r)


def test_str_contains_total_runs():
    r = _make_result(total_runs=42)
    assert "42" in str(r)


def test_str_contains_busiest_hour():
    r = _make_result(busiest_hour=9, runs_per_hour={h: (60 if h == 9 else 0) for h in range(24)})
    assert "09:00" in str(r)


def test_str_contains_quietest_hour():
    r = _make_result(quietest_hour=3, runs_per_hour={h: (1 if h == 3 else 0) for h in range(24)})
    assert "03:00" in str(r)


def test_str_is_multiline():
    r = _make_result()
    assert "\n" in str(r)


def test_str_has_at_least_four_lines():
    r = _make_result()
    assert len(str(r).splitlines()) >= 4
