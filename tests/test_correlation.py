import pytest
from csvwrangler.correlation import (
    correlate_pair,
    correlate_matrix,
    correlate_all,
    _pearson,
    _numeric_values,
)


def _rows():
    return [
        {"x": "1", "y": "2", "z": "3", "label": "a"},
        {"x": "2", "y": "4", "z": "1", "label": "b"},
        {"x": "3", "y": "6", "z": "2", "label": "c"},
        {"x": "4", "y": "8", "z": "4", "label": "d"},
        {"x": "5", "y": "10", "z": "5", "label": "e"},
    ]


def test_perfect_positive_correlation():
    rows = _rows()
    result = correlate_pair(rows, "x", "y")
    assert result["col_a"] == "x"
    assert result["col_b"] == "y"
    assert abs(float(result["r"]) - 1.0) < 1e-5


def test_imperfect_correlation_between_zero_and_one():
    rows = _rows()
    result = correlate_pair(rows, "x", "z")
    r = float(result["r"])
    assert 0.0 < r < 1.0


def test_non_numeric_column_returns_empty():
    rows = _rows()
    result = correlate_pair(rows, "x", "label")
    assert result["r"] == ""


def test_constant_column_returns_empty():
    rows = [{"a": "5", "b": str(i)} for i in range(5)]
    result = correlate_pair(rows, "a", "b")
    assert result["r"] == ""


def test_too_few_rows_returns_empty():
    rows = [{"a": "1", "b": "2"}]
    result = correlate_pair(rows, "a", "b")
    assert result["r"] == ""


def test_matrix_returns_correct_pair_count():
    rows = _rows()
    results = correlate_matrix(rows, ["x", "y", "z"])
    # 3 choose 2 = 3 pairs
    assert len(results) == 3


def test_matrix_field_names():
    rows = _rows()
    results = correlate_matrix(rows, ["x", "y"])
    assert results[0]["col_a"] == "x"
    assert results[0]["col_b"] == "y"


def test_correlate_all_skips_string_columns():
    rows = _rows()
    results = correlate_all(rows)
    col_pairs = [(r["col_a"], r["col_b"]) for r in results]
    for a, b in col_pairs:
        assert a != "label" and b != "label"


def test_correlate_all_empty_rows():
    assert correlate_all([]) == []


def test_numeric_values_with_non_numeric():
    rows = [{"v": "1"}, {"v": "abc"}, {"v": "3"}]
    vals = _numeric_values(rows, "v")
    assert vals[0] == 1.0
    assert vals[1] is None
    assert vals[2] == 3.0
