"""Annotate a cron expression with inline field-level comments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from cronlens.parser import CronExpression, CronParseError
from cronlens.explainer import _explain_field

_FIELD_NAMES = ["minute", "hour", "day", "month", "weekday"]


@dataclass
class AnnotatedField:
    """A single field with its raw token and a human-readable annotation."""

    name: str
    token: str
    annotation: str

    def __str__(self) -> str:
        return f"{self.token:<12}# {self.name}: {self.annotation}"


@dataclass
class AnnotationResult:
    """Full annotation for a cron expression."""

    expression: str
    fields: List[AnnotatedField]

    def __str__(self) -> str:
        lines = [f"# {self.expression}"]
        for field in self.fields:
            lines.append(str(field))
        return "\n".join(lines)


def annotate(expression: str) -> AnnotationResult:
    """Parse *expression* and return an :class:`AnnotationResult`.

    Raises :class:`~cronlens.parser.CronParseError` for invalid input.
    """
    expr = CronExpression(expression)
    tokens = expression.split()
    fields: List[AnnotatedField] = []
    field_objects = [
        expr.minute,
        expr.hour,
        expr.day,
        expr.month,
        expr.weekday,
    ]
    for name, token, field_obj in zip(_FIELD_NAMES, tokens, field_objects):
        annotation = _explain_field(name, field_obj)
        fields.append(AnnotatedField(name=name, token=token, annotation=annotation))
    return AnnotationResult(expression=expression, fields=fields)
