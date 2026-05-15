"""Heatmap: show run frequency across hours-of-day and days-of-week."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

from cronlens.parser import CronExpression
from cronlens.next_run import iter_next_runs

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
HOURS = list(range(24))


@dataclass
class HeatmapResult:
    expression: str
    # grid[weekday_0indexed][hour] = count
    grid: List[List[int]] = field(default_factory=lambda: [[0] * 24 for _ in range(7)])
    window_days: int = 7

    def peak(self) -> int:
        return max(v for row in self.grid for v in row)

    def total(self) -> int:
        return sum(v for row in self.grid for v in row)

    def __str__(self) -> str:
        peak = self.peak() or 1
        shades = " ░▒▓█"
        lines = [f"Heatmap for: {self.expression}  (window: {self.window_days}d)"]
        header = "     " + "".join(f"{h:02d}" for h in HOURS)
        lines.append(header)
        for di, day in enumerate(DAYS):
            row = ""
            for h in HOURS:
                count = self.grid[di][h]
                idx = min(int(count / peak * (len(shades) - 1)), len(shades) - 1)
                row += shades[idx] * 2
            lines.append(f"{day}  {row}")
        lines.append(f"Total runs in window: {self.total()}")
        return "\n".join(lines)


def build_heatmap(expr: CronExpression, window_days: int = 7) -> HeatmapResult:
    """Count runs per (weekday, hour) cell over *window_days* days."""
    if window_days < 1:
        raise ValueError("window_days must be >= 1")
    ref = datetime.now().replace(second=0, microsecond=0)
    limit = ref + timedelta(days=window_days)
    result = HeatmapResult(expression=str(expr), window_days=window_days)
    for run in iter_next_runs(expr, ref=ref):
        if run >= limit:
            break
        # Monday=0 … Sunday=6  (matches our DAYS list)
        result.grid[run.weekday()][run.hour] += 1
    return result
