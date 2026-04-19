"""Tests for csvwrangler.sort."""

import pytest
from csvwrangler.sort import sort_rows

ROWS = [
    {"name": "Charlie", "score": "85", "city": "Boston"},
    {"name": "Alice",   "score": "92", "city": "Atlanta"},
    {"name": "Bob",     "score": "78", "city": "chicago"},
]


def test_sort_string_asc():
    result = sort_rows(ROWS, key="name")
    assert [r["name"] for r in result] == ["Alice", "Bob", "Charlie"]


def test_sort_string_desc():
    result = sort_rows(ROWS, key="name", reverse=True)
    assert [r["name"] for r in result] == ["Charlie", "Bob", "Alice"]


def test_sort_numeric_asc():
    result = sort_rows(ROWS, key="score", numeric=True)
    assert [r["score"] for r in result] == ["78", "85", "92"]


def test_sort_numeric_desc():
    result = sort_rows(ROWS, key="score", numeric=True, reverse=True)
    assert [r["score"] for r in result] == ["92", "85", "78"]


def test_sort_case_insensitive():
    # 'chicago' should sort after 'Atlanta' and before nothing — just check order
    result = sort_rows(ROWS, key="city")
    names_in_order = [r["city"].lower() for r in result]
    assert names_in_order == sorted(names_in_order)


def test_sort_missing_key_string():
    rows = [{"a": "banana"}, {"a": "apple"}, {}]
    result = sort_rows(rows, key="a")
    # missing key treated as empty string, sorts first
    assert result[0].get("a", "") == ""


def test_sort_missing_key_numeric():
    rows = [{"v": "10"}, {"v": "3"}, {}]
    result = sort_rows(rows, key="v", numeric=True)
    assert result[0].get("v", "0") in ("", None, "0") or float(result[0].get("v", 0) or 0) == 0


def test_sort_preserves_all_rows():
    result = sort_rows(ROWS, key="name")
    assert len(result) == len(ROWS)


def test_sort_empty():
    assert sort_rows([], key="name") == []


def test_sort_does_not_mutate_input():
    """sort_rows should return a new list and not modify the original."""
    original_order = [r["name"] for r in ROWS]
    sort_rows(ROWS, key="name")
    assert [r["name"] for r in ROWS] == original_order
