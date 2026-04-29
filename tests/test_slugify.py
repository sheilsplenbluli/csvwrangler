import pytest
from csvwrangler.slugify import _slugify_value, slugify_column, slugify_many


def _rows():
    return [
        {"id": "1", "title": "Hello World"},
        {"id": "2", "title": "  Spaces  Around  "},
        {"id": "3", "title": "Café & Bar!"},
        {"id": "4", "title": "Already-a-slug"},
        {"id": "5", "title": ""},
    ]


def test_basic_lowercase_hyphen():
    assert _slugify_value("Hello World") == "hello-world"


def test_strips_leading_trailing_spaces():
    assert _slugify_value("  hello  ") == "hello"


def test_multiple_spaces_become_single_separator():
    assert _slugify_value("a   b") == "a-b"


def test_custom_separator_underscore():
    assert _slugify_value("hello world", separator="_") == "hello_world"


def test_uppercase_preserved_when_lowercase_false():
    result = _slugify_value("Hello World", lowercase=False)
    assert result == "Hello-World"


def test_special_chars_removed():
    result = _slugify_value("Café & Bar!")
    assert "!" not in result
    assert "&" not in result


def test_accented_char_replaced():
    result = _slugify_value("café")
    assert result == "cafe"


def test_max_length_truncates():
    result = _slugify_value("hello world foo bar", max_length=10)
    assert len(result) <= 10


def test_max_length_does_not_end_with_separator():
    result = _slugify_value("hello world", separator="-", max_length=7)
    assert not result.endswith("-")


def test_empty_string_passthrough():
    assert _slugify_value("") == ""


def test_slugify_column_overwrites_in_place():
    rows = [{"name": "Hello World"}, {"name": "Foo Bar"}]
    result = slugify_column(rows, "name")
    assert result[0]["name"] == "hello-world"
    assert result[1]["name"] == "foo-bar"


def test_slugify_column_dest_column():
    rows = [{"title": "Hello World"}]
    result = slugify_column(rows, "title", dest="slug")
    assert result[0]["title"] == "Hello World"
    assert result[0]["slug"] == "hello-world"


def test_slugify_column_does_not_mutate_original():
    rows = [{"name": "Hello World"}]
    original = rows[0].copy()
    slugify_column(rows, "name", dest="slug")
    assert rows[0] == original


def test_slugify_column_missing_column_returns_empty():
    rows = [{"other": "value"}]
    result = slugify_column(rows, "name")
    assert result[0]["name"] == ""


def test_slugify_many_applies_to_all_columns():
    rows = [{"a": "Hello World", "b": "Foo Bar"}]
    result = slugify_many(rows, ["a", "b"])
    assert result[0]["a"] == "hello-world"
    assert result[0]["b"] == "foo-bar"


def test_slugify_many_empty_column_list_returns_unchanged():
    rows = [{"a": "Hello World"}]
    result = slugify_many(rows, [])
    assert result[0]["a"] == "Hello World"


def test_already_slugified_unchanged():
    assert _slugify_value("already-a-slug") == "already-a-slug"
