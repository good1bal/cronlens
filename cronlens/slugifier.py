"""Slugifier: convert a cron expression into a human-friendly slug identifier."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from cronlens.parser import CronExpression, CronParseError
from cronlens.classifier import classify


@dataclass
class SlugResult:
    expression: str
    slug: str
    tokens: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        return (
            f"Expression : {self.expression}\n"
            f"Slug       : {self.slug}\n"
            f"Tokens     : {' | '.join(self.tokens)}"
        )


def _field_slug(token: str, name: str) -> str:
    """Return a short slug fragment for a single cron field token."""
    if token == "*":
        return f"every-{name}"
    if token.startswith("*/"):
        step = token[2:]
        return f"every-{step}-{name}s"
    if "-" in token and "," not in token:
        start, end = token.split("-", 1)
        return f"{name}-{start}-to-{end}"
    if "," in token:
        parts = token.split(",")
        return f"{name}-" + "-".join(parts)
    return f"{name}-{token}"


FIELD_NAMES = ["minute", "hour", "dom", "month", "dow"]


def slugify(expression: str) -> SlugResult:
    """Convert *expression* into a URL/filename-safe slug.

    Raises ``CronParseError`` if the expression is invalid.
    """
    expr = CronExpression(expression)  # raises CronParseError on bad input
    raw_fields = expression.split()

    tokens: List[str] = []
    for token, name in zip(raw_fields, FIELD_NAMES):
        tokens.append(_field_slug(token, name))

    # Prefix with the classifier category for extra context
    result = classify(expr)
    category_slug = result.category.lower().replace(" ", "-")

    slug = category_slug + "--" + "__".join(tokens)
    # Sanitise: keep only alphanumeric, hyphens, underscores
    slug = "".join(c if c in "-_" or c.isalnum() else "-" for c in slug)
    slug = slug.strip("-")

    return SlugResult(expression=expression, slug=slug, tokens=tokens)
