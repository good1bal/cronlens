"""High-level linter that combines validation with semantic warnings."""

from dataclasses import dataclass, field
from typing import List

from cronlens.validator import validate, ValidationResult


@dataclass
class LintWarning:
    field_name: str
    message: str

    def __str__(self) -> str:
        return f"[{self.field_name}] {self.message}"


@dataclass
class LintResult:
    expression: str
    validation: ValidationResult
    warnings: List[LintWarning] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """True when the expression is syntactically valid (warnings allowed)."""
        return self.validation.valid

    def has_warnings(self) -> bool:
        return len(self.warnings) > 0

    def report(self) -> str:
        lines = [f"Expression : {self.expression}"]
        if self.ok:
            lines.append("Status     : valid")
        else:
            lines.append("Status     : INVALID")
            for err in self.validation.errors:
                lines.append(f"  ERROR  - {err}")
        for w in self.warnings:
            lines.append(f"  WARN   - {w}")
        return "\n".join(lines)


def _semantic_warnings(parts: List[str]) -> List[LintWarning]:
    warnings: List[LintWarning] = []
    minute, hour, day, month, weekday = parts

    # Warn when both day-of-month and day-of-week are set (ambiguous behaviour)
    if day != "*" and weekday != "*":
        warnings.append(
            LintWarning(
                "day/weekday",
                "both day-of-month and day-of-week are restricted; "
                "most cron implementations use OR semantics which may be unintended",
            )
        )

    # Warn about very-high-frequency expressions (every minute)
    if minute == "*" and hour == "*":
        warnings.append(
            LintWarning("minute", "expression runs every minute — ensure this is intentional")
        )

    # Warn about Feb 30/31 impossibility
    if month == "2" and day not in ("*",) and any(
        int(d) > 28 for d in day.split(",") if d.isdigit()
    ):
        warnings.append(
            LintWarning("day", "day > 28 in February will never match in non-leap years")
        )

    return warnings


def lint(expression: str) -> LintResult:
    """Validate and apply semantic checks to a cron expression."""
    validation = validate(expression)
    parts = expression.strip().split()
    warnings: List[LintWarning] = []
    if validation.valid and len(parts) == 5:
        warnings = _semantic_warnings(parts)
    return LintResult(expression=expression, validation=validation, warnings=warnings)
