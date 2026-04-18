"""Tests for csvwrangler.summarize."""

import pytest
from csvwrangler.summarize import summarize_column, summarize_all

NUMERIC_ROWS = [
    {"name": "Alice", "score": "90"},
    {"name": "Bob",   "score": "80"},
    {"name": "Carol", "score": "70"},
    {"name": "Dave",  "score": "100"},
]

STRING_ROWS = [
    {"city": "London"},
    {"city": "Paris"},
    {"city": "London"},
    {"city": "Berlin"},
]

MISSING_ROWS = [
    {"val": "1"},
    {"val": ""},
    {"val": "3"},
    {"val": ""},
]


def test_numeric_mean():
    s = summarize_column(NUMERIC_ROWS, "score")
    assert s["mean"] == 85.0


def test_numeric_min_max():
    s = summarize_column(NUMERIC_ROWS, "score")
    assert s["min"] == 70.0
    assert s["max"] == 100.0


def test_numeric_median_even():
    s = summarize_column(NUMERIC_ROWS, "score")
    assert s["median"] == 85.0


def test_numeric_median_odd():
    rows = [{"v": "1"}, {"v": "2"}, {"v": "3"}]
    s = summarize_column(rows, "v")
    assert s["median"] == 2.0


def test_string_unique():
    s = summarize_column(STRING_ROWS, "city")
    assert s["unique"] == 3


def test_string_top():
    s = summarize_column(STRING_ROWS, "city")
    assert s["top"] == "London"
    assert s["top_count"] == 2


def test_missing_count():
    s = summarize_column(MISSING_ROWS, "val")
    assert s["missing"] == 2


def test_empty_rows():
    assert summarize_column([], "x") == {"column": "x", "count": 0}


def test_summarize_all_columns():
    result = summarize_all(NUMERIC_ROWS)
    cols = [r["column"] for r in result]
    assert cols == ["name", "score"]


def test_summarize_all_empty():
    assert summarize_all([]) == []
