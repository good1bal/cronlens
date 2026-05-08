"""Human-readable explanation of cron expression fields."""

from cronlens.parser import CronExpression

_WEEKDAY_NAMES = [
    "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
]

_MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


def _explain_field(values: set[int], min_val: int, max_val: int, unit: str,
                   names: list[str] | None = None) -> str:
    all_values = set(range(min_val, max_val + 1))
    if values == all_values:
        return f"every {unit}"

    if names:
        labels = [names[v] for v in sorted(values)]
    else:
        labels = [str(v) for v in sorted(values)]

    if len(labels) == 1:
        return f"{unit} {labels[0]}"
    return f"{unit}s {', '.join(labels[:-1])} and {labels[-1]}"


def explain(expr: CronExpression) -> str:
    """Return a plain-English description of a CronExpression."""
    parts = []

    minute_part = _explain_field(expr.minutes, 0, 59, "minute")
    hour_part = _explain_field(expr.hours, 0, 23, "hour")
    dom_part = _explain_field(expr.days_of_month, 1, 31, "day-of-month")
    month_part = _explain_field(expr.months, 1, 12, "month", _MONTH_NAMES)
    dow_part = _explain_field(expr.days_of_week, 0, 6, "weekday", _WEEKDAY_NAMES)

    all_minutes = expr.minutes == set(range(0, 60))
    all_hours = expr.hours == set(range(0, 24))
    all_dom = expr.days_of_month == set(range(1, 32))
    all_months = expr.months == set(range(1, 13))
    all_dow = expr.days_of_week == set(range(0, 7))

    if all_minutes and all_hours and all_dom and all_months and all_dow:
        return "Runs every minute."

    if not all_minutes:
        parts.append(f"at {minute_part}")
    if not all_hours:
        parts.append(f"past {hour_part}")
    if not all_dom:
        parts.append(f"on {dom_part}")
    if not all_months:
        parts.append(f"in {month_part}")
    if not all_dow:
        parts.append(f"on {dow_part}")

    if not parts:
        return "Runs every minute."

    return "Runs " + ", ".join(parts) + "."
