"""Tests for csvwrangler.filters module."""

import pytest
from csvwrangler.filters import build_filter, apply_filters

SAMPLE_ROWS = [
    {"name": "Alice", "age": "30", "city": "New York"},
    {"name": "Bob", "age": "25", "city": "Los Angeles"},
    {"name": "Charlie", "age": "35", "city": "New York"},
    {"name": "Diana", "age": "28", "city": "Chicago"},
]


def test_eq_string():
    f = build_filter("city", "eq", "New York")
    result = apply_filters(SAMPLE_ROWS, [f])
    assert len(result) == 2
    assert all(r["city"] == "New York" for r in result)


def test_gt_numeric():
    f = build_filter("age", "gt", "28")
    result = apply_filters(SAMPLE_ROWS, [f])
    assert {r["name"] for r in result} == {"Alice", "Charlie"}


def test_lte_numeric():
    f = build_filter("age", "lte", "28")
    result = apply_filters(SAMPLE_ROWS, [f])
    assert {r["name"] for r in result} == {"Bob", "Diana"}


def test_contains():
    f = build_filter("city", "contains", "Angeles")
    result = apply_filters(SAMPLE_ROWS, [f])
    assert len(result) == 1
    assert result[0]["name"] == "Bob"


def test_startswith():
    f = build_filter("name", "startswith", "Ch")
    result = apply_filters(SAMPLE_ROWS, [f])
    assert result[0]["name"] == "Charlie"


def test_multiple_filters():
    f1 = build_filter("city", "eq", "New York")
    f2 = build_filter("age", "gt", "30")
    result = apply_filters(SAMPLE_ROWS, [f1, f2])
    assert len(result) == 1
    assert result[0]["name"] == "Charlie"


def test_unknown_operator_raises():
    with pytest.raises(ValueError, match="Unknown operator"):
        build_filter("age", "between", "20")


def test_missing_column_raises():
    f = build_filter("salary", "eq", "1000")
    with pytest.raises(KeyError, match="salary"):
        apply_filters(SAMPLE_ROWS, [f])


def test_no_matches_returns_empty():
    f = build_filter("age", "gt", "100")
    result = apply_filters(SAMPLE_ROWS, [f])
    assert result == []
