"""Tests for GroupResult.__str__ and helper properties."""

from cronlens.grouper import GroupResult, group


def test_str_contains_category_header():
    result = group(["* * * * *"])
    text = str(result)
    assert "every-minute" in text


def test_str_contains_expression():
    result = group(["0 9 * * *"])
    text = str(result)
    assert "0 9 * * *" in text


def test_str_contains_invalid_section_when_present():
    result = group(["bad"])
    text = str(result)
    assert "invalid" in text
    assert "bad" in text


def test_str_no_invalid_section_when_all_valid():
    result = group(["* * * * *"])
    text = str(result)
    assert "invalid" not in text


def test_str_empty_input_is_empty_string():
    result = group([])
    assert str(result) == ""


def test_group_result_category_names_empty_when_no_groups():
    result = GroupResult()
    assert result.category_names == []


def test_group_result_invalid_default_empty():
    result = GroupResult()
    assert result.invalid == []
