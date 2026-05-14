"""Focused __str__ / formatting tests for AnnotationResult and AnnotatedField."""

from cronlens.annotator import annotate, AnnotatedField


def test_annotated_field_str_format_has_hash_comment():
    result = annotate("0 12 * * *")
    for field in result.fields:
        assert "#" in str(field)


def test_annotated_field_str_token_is_left_aligned():
    """Token should be padded so annotations line up."""
    result = annotate("*/5 * * * *")
    minute_field = result.fields[0]
    text = str(minute_field)
    # token comes before the '#'
    hash_pos = text.index("#")
    assert hash_pos >= len("*/5")


def test_result_str_first_line_is_header():
    expr = "0 0 1 1 *"
    result = annotate(expr)
    first_line = str(result).splitlines()[0]
    assert first_line.startswith("#")
    assert expr in first_line


def test_result_str_remaining_lines_contain_tokens():
    expr = "30 8 * * 1-5"
    result = annotate(expr)
    body_lines = str(result).splitlines()[1:]
    tokens = ["30", "8", "*", "*", "1-5"]
    for line, token in zip(body_lines, tokens):
        assert token in line


def test_result_str_line_count():
    result = annotate("0 6 * * 0")
    assert len(str(result).splitlines()) == 6


def test_annotated_field_repr_contains_name():
    field = AnnotatedField(name="minute", token="0", annotation="at minute 0")
    # __str__ should at least mention the name
    assert "minute" in str(field)


def test_every_minute_annotation_mentions_every():
    result = annotate("* * * * *")
    minute_field = result.fields[0]
    assert "every" in minute_field.annotation.lower()
