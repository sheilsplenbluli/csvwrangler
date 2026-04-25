import pytest
from csvwrangler.correlation import correlate_pair, correlate_matrix, correlate_all


def test_negative_correlation():
    rows = [
        {"a": str(i), "b": str(10 - i)}
        for i in range(1, 7)
    ]
    result = correlate_pair(rows, "a", "b")
    r = float(result["r"])
    assert r < -0.99


def test_missing_values_skipped():
    rows = [
        {"a": "1", "b": "2"},
        {"a": "", "b": "4"},
        {"a": "3", "b": "6"},
        {"a": "4", "b": ""},
        {"a": "5", "b": "10"},
    ]
    result = correlate_pair(rows, "a", "b")
    # Should still compute from valid pairs
    assert result["r"] != ""


def test_single_column_matrix_returns_empty():
    rows = [{"x": str(i)} for i in range(5)]
    results = correlate_matrix(rows, ["x"])
    assert results == []


def test_correlate_all_single_numeric_column():
    rows = [{"x": str(i), "label": "a"} for i in range(5)]
    results = correlate_all(rows)
    assert results == []


def test_r_precision():
    rows = [
        {"a": "1", "b": "1"},
        {"a": "2", "b": "2"},
        {"a": "3", "b": "3"},
    ]
    result = correlate_pair(rows, "a", "b")
    # Should have 6 decimal places
    assert len(result["r"].split(".")[1]) == 6


def test_does_not_mutate_input():
    rows = [{"x": str(i), "y": str(i * 2)} for i in range(5)]
    original = [dict(r) for r in rows]
    correlate_all(rows)
    assert rows == original
