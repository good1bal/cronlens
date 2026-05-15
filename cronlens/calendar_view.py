"""Weekly calendar view showing which hours/days a cron expression fires."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

from cronlens.parser import CronExpression
from cronlens.next_run import iter_next_runs

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


@dataclass
class CalendarResult:
    expression: str
    # grid[day_of_week 0-6][hour 0-23] = fire count
    grid: List[List[int]] = field(default_factory=lambda: [[0] * 24 for _ in range(7)])
    weeks: int = 1

    @property
    def peak(self) -> int:
        return max(cell for row in self.grid for cell in row)

    @property
    def total(self) -> int:
        return sum(cell for row in self.grid for cell in row)

    def __str__(self) -> str:
        lines = [f"Calendar view for: {self.expression}  (over {self.weeks} week(s))"]
        header = "     " + "".join(f"{h:>3}" for h in range(24))
        lines.append(header)
        pk = self.peak or 1
        for dow, name in enumerate(DAY_NAMES):
            cells = ""
            for hour in range(24):
                v = self.grid[dow][hour]
                if v == 0:
                    cells += "  ."
                elif v / pk < 0.5:
                    cells += "  +"
                else:
                    cells += "  #"
            lines.append(f"{name} {cells}")
        lines.append(f"Total fires: {self.total}  Peak slot: {self.peak}")
        return "\n".join(lines)


def build_calendar(expr: CronExpression, weeks: int = 1) -> CalendarResult:
    """Return a CalendarResult for *expr* over the given number of weeks."""
    if weeks < 1:
        raise ValueError("weeks must be >= 1")
    result = CalendarResult(expression=str(expr), weeks=weeks)
    ref = datetime.now().replace(second=0, microsecond=0)
    limit = ref + timedelta(weeks=weeks)
    for dt in iter_next_runs(expr, n=weeks * 7 * 24 * 60, ref=ref):
        if dt >= limit:
            break
        dow = dt.weekday()  # 0=Monday
        result.grid[dow][dt.hour] += 1
    return result
