"""Tests for csvwrangler/schema.py."""

import pytest
from csvwrangler.schema import validate_schema, schema_summary


def _rows(*dicts):
    return list(dicts)


def test_valid_int_passes():
    rows = _rows({"age": "25"}, {"age": "30"})
    errors = validate_schema(rows, {"age": "int"})
    assert errors == []


def test_invalid_int_caught():
    rows = _rows({"age": "twenty"}, {"age": "30"})
    errors = validate_schema(rows, {"age": "int"})
    assert len(errors) == 1
    assert errors[0]["column"] == "age"
    assert errors[0]["row"] == 1
    assert errors[0]["expected"] == "int"


def test_valid_float_passes():
    rows = _rows({"score": "3.14"}, {"score": "2.71"})
    errors = validate_schema(rows, {"score": "float"})
    assert errors == []


def test_invalid_float_caught():
    rows = _rows({"score": "abc"})
    errors = validate_schema(rows, {"score": "float"})
    assert len(errors) == 1
    assert errors[0]["value"] == "abc"


def test_nonempty_passes_when_filled():
    rows = _rows({"name": "Alice"}, {"name": "Bob"})
    errors = validate_schema(rows, {"name": "nonempty"})
    assert errors == []


def test_nonempty_fails_on_empty_string():
    rows = _rows({"name": ""}, {"name": "Bob"})
    errors = validate_schema(rows, {"name": "nonempty"})
    assert len(errors) == 1
    assert errors[0]["row"] == 1


def test_nonempty_fails_on_whitespace_only():
    rows = _rows({"name": "   "})
    errors = validate_schema(rows, {"name": "nonempty"})
    assert len(errors) == 1


def test_str_type_always_passes():
    rows = _rows({"note": ""}, {"note": "anything"}, {"note": "123"})
    errors = validate_schema(rows, {"note": "str"})
    assert errors == []


def test_missing_column_treated_as_empty():
    rows = _rows({"other": "x"})
    errors = validate_schema(rows, {"age": "int"})
    assert len(errors) == 1
    assert errors[0]["value"] == ""


def test_multiple_columns_multiple_errors():
    rows = _rows({"age": "bad", "score": "also_bad"})
    errors = validate_schema(rows, {"age": "int", "score": "float"})
    assert len(errors) == 2


def test_row_number_is_one_indexed():
    rows = _rows({"x": "ok"}, {"x": "ok"}, {"x": "bad"})
    errors = validate_schema(rows, {"x": "int"})
    assert errors[0]["row"] == 3


def test_unknown_type_raises():
    rows = _rows({"x": "1"})
    with pytest.raises(ValueError, match="Unknown type"):
        validate_schema(rows, {"x": "boolean"})


def test_schema_summary_no_errors():
    summary = schema_summary([])
    assert summary["passed"] is True
    assert summary["total_errors"] == 0
    assert summary["by_column"] == {}


def test_schema_summary_counts_by_column():
    errors = [
        {"row": 1, "column": "age", "value": "x", "expected": "int"},
        {"row": 2, "column": "age", "value": "y", "expected": "int"},
        {"row": 1, "column": "score", "value": "z", "expected": "float"},
    ]
    summary = schema_summary(errors)
    assert summary["total_errors"] == 3
    assert summary["by_column"]["age"] == 2
    assert summary["by_column"]["score"] == 1
    assert summary["passed"] is False
