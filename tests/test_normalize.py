import pytest
from csvwrangler.normalize import minmax_normalize, zscore_normalize, normalize_many


def _rows(*vals):
    return [{"x": str(v)} for v in vals]


def test_minmax_basic():
    rows = _rows(0, 5, 10)
    result = minmax_normalize(rows, "x")
    assert result[0]["x"] == "0.0"
    assert result[1]["x"] == "0.5"
    assert result[2]["x"] == "1.0"


def test_minmax_dest_column():
    rows = _rows(0, 10)
    result = minmax_normalize(rows, "x", dest="x_norm")
    assert "x" in result[0]
    assert result[0]["x_norm"] == "0.0"
    assert result[1]["x_norm"] == "1.0"


def test_minmax_all_same_values():
    rows = _rows(5, 5, 5)
    result = minmax_normalize(rows, "x")
    assert all(r["x"] == "" for r in result)


def test_minmax_non_numeric_becomes_empty():
    rows = [{"x": "abc"}, {"x": "2"}, {"x": ""}]
    result = minmax_normalize(rows, "x")
    assert result[0]["x"] == ""
    assert result[2]["x"] == ""


def test_minmax_does_not_mutate():
    rows = [{"x": "1"}, {"x": "2"}]
    original = [{"x": "1"}, {"x": "2"}]
    minmax_normalize(rows, "x")
    assert rows == original


def test_zscore_basic():
    rows = _rows(2, 4, 6)
    result = zscore_normalize(rows, "x")
    scores = [float(r["x"]) for r in result]
    assert abs(sum(scores)) < 1e-5
    assert scores[2] > scores[1] > scores[0]


def test_zscore_uniform_data():
    rows = _rows(3, 3, 3)
    result = zscore_normalize(rows, "x")
    assert all(r["x"] == "" for r in result)


def test_zscore_non_numeric_becomes_empty():
    rows = [{"x": "hello"}, {"x": "10"}]
    result = zscore_normalize(rows, "x")
    assert result[0]["x"] == ""


def test_zscore_dest_column():
    rows = _rows(1, 2, 3)
    result = zscore_normalize(rows, "x", dest="z")
    assert "x" in result[0]
    assert "z" in result[0]


def test_normalize_many_mixed():
    rows = [{"a": "10", "b": "100"}, {"a": "20", "b": "200"}]
    specs = [
        {"column": "a", "method": "minmax"},
        {"column": "b", "method": "zscore", "dest": "b_z"},
    ]
    result = normalize_many(rows, specs)
    assert result[0]["a"] == "0.0"
    assert result[1]["a"] == "1.0"
    assert "b_z" in result[0]
    assert "b" in result[0]
