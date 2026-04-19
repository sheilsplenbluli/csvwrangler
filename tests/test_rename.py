"""Tests for csvwrangler/rename.py."""
import pytest
from csvwrangler.rename import rename_columns, rename_prefix, rename_strip, rename_pattern

ROWS = [
    {"first_name": "Alice", "last_name": "Smith", "age": "30"},
    {"first_name": "Bob",   "last_name": "Jones", "age": "25"},
]


def test_rename_columns_basic():
    result = rename_columns(ROWS, {"first_name": "fname", "last_name": "lname"})
    assert result[0] == {"fname": "Alice", "lname": "Smith", "age": "30"}


def test_rename_columns_partial():
    result = rename_columns(ROWS, {"age": "years"})
    assert "years" in result[0]
    assert "age" not in result[0]
    assert "first_name" in result[0]


def test_rename_columns_unknown_key_ignored():
    result = rename_columns(ROWS, {"nonexistent": "x"})
    assert list(result[0].keys()) == ["first_name", "last_name", "age"]


def test_rename_columns_does_not_mutate():
    original = [{"a": "1", "b": "2"}]
    rename_columns(original, {"a": "z"})
    assert "a" in original[0]


def test_rename_prefix_all_columns():
    result = rename_prefix(ROWS, "col_")
    assert set(result[0].keys()) == {"col_first_name", "col_last_name", "col_age"}


def test_rename_prefix_selected_columns():
    result = rename_prefix(ROWS, "x_", columns=["age"])
    assert "x_age" in result[0]
    assert "first_name" in result[0]
    assert "x_first_name" not in result[0]


def test_rename_strip_whitespace():
    rows = [{" name ": "Alice", "  age  ": "30"}]
    result = rename_strip(rows)
    assert list(result[0].keys()) == ["name", "age"]


def test_rename_strip_custom_chars():
    rows = [{"__name__": "Alice"}]
    result = rename_strip(rows, chars="_")
    assert "name" in result[0]


def test_rename_pattern_basic():
    result = rename_pattern(ROWS, r"_name$", "")
    assert "first" in result[0]
    assert "last" in result[0]
    assert "age" in result[0]


def test_rename_pattern_no_match_unchanged():
    result = rename_pattern(ROWS, r"zzz", "X")
    assert list(result[0].keys()) == ["first_name", "last_name", "age"]


def test_rename_empty_rows():
    assert rename_columns([], {"a": "b"}) == []
    assert rename_prefix([], "p_") == []
    assert rename_strip([]) == []
    assert rename_pattern([], "x", "y") == []
