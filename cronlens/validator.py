"""Cron expression validator with detailed field-level diagnostics."""

from dataclasses import dataclass, field
from typing import List, Optional

FIELD_NAMES = ["minute", "hour", "day", "month", "weekday"]
FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day": (1, 31),
    "month": (1, 12),
    "weekday": (0, 7),
}


@dataclass
class FieldError:
    field_name: str
    raw_value: str
    message: str

    def __str__(self) -> str:
        return f"[{self.field_name}] '{self.raw_value}': {self.message}"


@dataclass
class ValidationResult:
    valid: bool
    errors: List[FieldError] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.valid

    def error_summary(self) -> str:
        if not self.errors:
            return "No errors."
        return "\n".join(str(e) for e in self.errors)


def _validate_field(name: str, raw: str) -> Optional[FieldError]:
    lo, hi = FIELD_RANGES[name]

    if raw == "*":
        return None

    # step syntax: */n or value/n
    if "/" in raw:
        parts = raw.split("/", 1)
        step_str = parts[1]
        if not step_str.isdigit() or int(step_str) < 1:
            return FieldError(name, raw, f"step must be a positive integer, got '{step_str}'")
        base = parts[0]
        if base != "*":
            raw = base  # validate the base part below
        else:
            return None

    # comma-separated list
    tokens = raw.split(",")
    for token in tokens:
        # range syntax: a-b
        if "-" in token:
            bounds = token.split("-", 1)
            if len(bounds) != 2 or not bounds[0].isdigit() or not bounds[1].isdigit():
                return FieldError(name, raw, f"invalid range '{token}'")
            a, b = int(bounds[0]), int(bounds[1])
            if a > b:
                return FieldError(name, raw, f"range start {a} exceeds end {b}")
            if not (lo <= a <= hi) or not (lo <= b <= hi):
                return FieldError(name, raw, f"range {a}-{b} out of bounds [{lo},{hi}]")
        else:
            if not token.isdigit():
                return FieldError(name, raw, f"'{token}' is not a valid integer")
            val = int(token)
            if not (lo <= val <= hi):
                return FieldError(name, raw, f"value {val} out of bounds [{lo},{hi}]")
    return None


def validate(expression: str) -> ValidationResult:
    """Validate a raw cron expression string, returning a ValidationResult."""
    parts = expression.strip().split()
    if len(parts) != 5:
        err = FieldError(
            "expression",
            expression,
            f"expected 5 fields, got {len(parts)}",
        )
        return ValidationResult(valid=False, errors=[err])

    errors = []
    for name, raw in zip(FIELD_NAMES, parts):
        err = _validate_field(name, raw)
        if err:
            errors.append(err)

    return ValidationResult(valid=len(errors) == 0, errors=errors)
