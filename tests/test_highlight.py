"""Tests for csvwrangler/highlight.py"""

import pytest
from csvwrangler.highlight import highlight_rows, highlight_any


def _rows():
    return [
        {"name": "alice", "score": "90", "grade": "A"},
        {"name": "bob",   "score": "55", "grade": "C"},
        {"name": "carol", "score": "72", "grade": "B"},
        {"name": "dave",  "score": "55", "grade": "C"},
    ]


def test_flag_column_added():
    result = highlight_rows(_rows(), "score", "gt", "80")
    assert "_highlight" in result[0]


def test_gt_flags_correct_rows():
    result = highlight_rows(_rows(), "score", "gt", "80")
    flags = [r["_highlight"] for r in result]
    assert flags == ["1", "0", "0", "0"]


def test_lte_flags_correct_rows():
    result = highlight_rows(_rows(), "score", "lte", "55")
    flags = [r["_highlight"] for r in result]
    assert flags == ["0", "1", "0", "1"]


def test_eq_string():
    result = highlight_rows(_rows(), "grade", "eq", "C")
    flags = [r["_highlight"] for r in result]
    assert flags == ["0", "1", "0", "1"]


def test_ne_string():
    result = highlight_rows(_rows(), "grade", "ne", "C")
    flags = [r["_highlight"] for r in result]
    assert flags == ["1", "0", "1", "0"]


def test_contains():
    result = highlight_rows(_rows(), "name", "contains", "a")
    flags = [r["_highlight"] for r in result]
    assert flags == ["1", "0", "1", "1"]


def test_startswith():
    result = highlight_rows(_rows(), "name", "startswith", "a")
    flags = [r["_highlight"] for r in result]
    assert flags == ["1", "0", "0", "0"]


def test_endswith():
    result = highlight_rows(_rows(), "name", "endswith", "e")
    flags = [r["_highlight"] for r in result]
    assert flags == ["1", "0", "0", "1"]


def test_custom_flag_column_and_values():
    result = highlight_rows(
        _rows(), "score", "gte", "72",
        flag_column="flagged", true_value="yes", false_value="no"
    )
    assert result[0]["flagged"] == "yes"
    assert result[1]["flagged"] == "no"
    assert result[2]["flagged"] == "yes"


def test_does_not_mutate_original():
    rows = _rows()
    highlight_rows(rows, "score", "gt", "50")
    assert "_highlight" not in rows[0]


def test_non_numeric_op_returns_false():
    result = highlight_rows(_rows(), "grade", "gt", "B")
    # non-numeric comparison with gt → all false
    assert all(r["_highlight"] == "0" for r in result)


def test_highlight_any_basic():
    conditions = [
        {"column": "score", "op": "gt", "operand": "85"},
        {"column": "grade", "op": "eq",  "operand": "C"},
    ]
    result = highlight_any(_rows(), conditions)
    flags = [r["_highlight"] for r in result]
    # alice score>85 → yes; bob grade==C → yes; carol neither → no; dave grade==C → yes
    assert flags == ["1", "1", "0", "1"]


def test_highlight_any_no_conditions_flags_nothing():
    result = highlight_any(_rows(), [])
    assert all(r["_highlight"] == "0" for r in result)


def test_empty_rows_returns_empty():
    assert highlight_rows([], "score", "gt", "50") == []
    assert highlight_any([], [{"column": "score", "op": "gt", "operand": "50"}]) == []
