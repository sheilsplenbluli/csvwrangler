"""Tests for csvwrangler/filters.py."""

import pytest
from csvwrangler.filters import build_filter, apply_filters

ROWS = [
    {"name": "Alice", "score": "90", "tag": "alpha"},
    {"name": "Bob", "score": "70", "tag": "beta"},
    {"name": "Carol", "score": "85", "tag": "alpha"},
    {"name": "Dave", "score": "70", "tag": "gamma"},
]


def test_eq_string():
    f = build_filter("name", "eq", "Alice")
    result = apply_filters(ROWS, [f])
    assert len(result) == 1 and result[0]["name"] == "Alice"


def test_gt_numeric():
    f = build_filter("score", "gt", "80")
    result = apply_filters(ROWS, [f])
    assert {r["name"] for r in result} == {"Alice", "Carol"}


def test_lte_numeric():
    f = build_filter("score", "lte", "70")
    result = apply_filters(ROWS, [f])
    assert {r["name"] for r in result} == {"Bob", "Dave"}


def test_contains():
    f = build_filter("tag", "contains", "lph")
    result = apply_filters(ROWS, [f])
    assert all(r["tag"] == "alpha" for r in result)
    assert len(result) == 2


def test_startswith():
    f = build_filter("tag", "startswith", "al")
    result = apply_filters(ROWS, [f])
    assert len(result) == 2


def test_neq():
    f = build_filter("name", "neq", "Bob")
    result = apply_filters(ROWS, [f])
    assert "Bob" not in {r["name"] for r in result}


def test_multiple_filters():
    f1 = build_filter("tag", "eq", "alpha")
    f2 = build_filter("score", "gt", "88")
    result = apply_filters(ROWS, [f1, f2])
    assert len(result) == 1 and result[0]["name"] == "Alice"


def test_unknown_op_raises():
    with pytest.raises(ValueError):
        build_filter("score", "unknown", "10")


def test_empty_rows():
    f = build_filter("score", "gt", "50")
    assert apply_filters([], [f]) == []
