"""Streak detector: finds consecutive run-day or run-hour streaks for a cron expression."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

from cronlens.parser import CronExpression
from cronlens.history import prev_runs


@dataclass
class StreakResult:
    expression: str
    window_days: int
    longest_day_streak: int
    longest_hour_streak: int
    active_days: int
    active_hours: int
    day_streaks: List[int] = field(default_factory=list)
    hour_streaks: List[int] = field(default_factory=list)

    def __str__(self) -> str:
        lines = [
            f"Expression : {self.expression}",
            f"Window     : {self.window_days} days",
            f"Active days: {self.active_days}",
            f"Active hrs : {self.active_hours}",
            f"Longest day streak : {self.longest_day_streak} day(s)",
            f"Longest hour streak: {self.longest_hour_streak} hour(s)",
        ]
        return "\n".join(lines)


def find_streaks(expr: CronExpression, window_days: int = 30, ref: datetime | None = None) -> StreakResult:
    """Compute consecutive-day and consecutive-hour streaks over *window_days* of history."""
    if window_days < 1:
        raise ValueError("window_days must be >= 1")

    ref = ref or datetime.now().replace(second=0, microsecond=0)
    total_minutes = window_days * 24 * 60
    runs = prev_runs(expr, n=total_minutes, ref=ref)

    # --- day streaks ---
    run_days = sorted({r.date() for r in runs})
    day_streaks: List[int] = []
    if run_days:
        streak = 1
        for i in range(1, len(run_days)):
            if (run_days[i] - run_days[i - 1]).days == 1:
                streak += 1
            else:
                day_streaks.append(streak)
                streak = 1
        day_streaks.append(streak)

    # --- hour streaks ---
    run_hours = sorted({r.replace(minute=0, second=0, microsecond=0) for r in runs})
    hour_streaks: List[int] = []
    if run_hours:
        streak = 1
        for i in range(1, len(run_hours)):
            if (run_hours[i] - run_hours[i - 1]) == timedelta(hours=1):
                streak += 1
            else:
                hour_streaks.append(streak)
                streak = 1
        hour_streaks.append(streak)

    return StreakResult(
        expression=repr(expr),
        window_days=window_days,
        longest_day_streak=max(day_streaks, default=0),
        longest_hour_streak=max(hour_streaks, default=0),
        active_days=len(run_days),
        active_hours=len(run_hours),
        day_streaks=day_streaks,
        hour_streaks=hour_streaks,
    )
