"""Convert a cron expression into a plain-English schedule description."""

from __future__ import annotations

from cronlens.parser import CronExpression

_MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

_WEEKDAY_NAMES = [
    "Sunday", "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday",
]


def _ordinal(n: int) -> str:
    """Return '1st', '2nd', '3rd', '4th', … for a given integer."""
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10 if n % 100 not in (11, 12, 13) else 0, "th")
    return f"{n}{suffix}"


def _values_sentence(values: list[int], name_map: list[str] | None = None) -> str:
    """Join a list of integers (or mapped names) with commas and 'and'."""
    if name_map:
        parts = [name_map[v] for v in values]
    else:
        parts = [str(v) for v in values]
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " and " + parts[-1]


def humanize(expr: CronExpression) -> str:
    """Return a single English sentence describing *expr*."""
    minute = expr.minute
    hour = expr.hour
    dom = expr.day_of_month
    month = expr.month
    dow = expr.day_of_week

    # ---- time part -------------------------------------------------------
    if minute.is_wildcard and hour.is_wildcard:
        time_part = "every minute"
    elif minute.is_wildcard:
        hour_str = _values_sentence(sorted(hour.values))
        time_part = f"every minute of hour {hour_str}"
    elif hour.is_wildcard:
        min_str = _values_sentence(sorted(minute.values))
        time_part = f"at minute {min_str} of every hour"
    else:
        times = [
            f"{h:02d}:{m:02d}"
            for h in sorted(hour.values)
            for m in sorted(minute.values)
        ]
        time_part = "at " + _values_sentence(times)

    # ---- day / month part ------------------------------------------------
    day_parts: list[str] = []

    if not month.is_wildcard:
        month_str = _values_sentence(sorted(month.values), _MONTH_NAMES)
        day_parts.append(f"in {month_str}")

    if not dom.is_wildcard and not dow.is_wildcard:
        dom_str = _values_sentence([_ordinal(d) for d in sorted(dom.values)])  # type: ignore[arg-type]
        dow_str = _values_sentence(sorted(dow.values), _WEEKDAY_NAMES)
        day_parts.append(f"on the {dom_str} if it falls on {dow_str}")
    elif not dom.is_wildcard:
        dom_str = _values_sentence([_ordinal(d) for d in sorted(dom.values)])  # type: ignore[arg-type]
        day_parts.append(f"on the {dom_str} of the month")
    elif not dow.is_wildcard:
        dow_str = _values_sentence(sorted(dow.values), _WEEKDAY_NAMES)
        day_parts.append(f"on {dow_str}")

    if day_parts:
        return time_part + ", " + ", ".join(day_parts)
    return time_part
