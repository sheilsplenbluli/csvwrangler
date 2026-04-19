import pytest
from csvwrangler.window import rolling_mean, rolling_sum, rolling_min, rolling_max


def _rows(vals):
    return [{"val": str(v)} for v in vals]


def test_rolling_mean_window_1():
    rows = _rows([1, 2, 3, 4])
    result = rolling_mean(rows, "val", window=1)
    assert [r["val_rolling_mean"] for r in result] == ["1.0", "2.0", "3.0", "4.0"]


def test_rolling_mean_window_3():
    rows = _rows([1, 2, 3, 4, 5])
    result = rolling_mean(rows, "val", window=3)
    means = [r["val_rolling_mean"] for r in result]
    assert means[0] == "1.0"
    assert means[1] == "1.5"
    assert means[2] == "2.0"
    assert means[3] == "3.0"
    assert means[4] == "4.0"


def test_rolling_sum_window_2():
    rows = _rows([10, 20, 30])
    result = rolling_sum(rows, "val", window=2)
    assert [r["val_rolling_sum"] for r in result] == ["10.0", "30.0", "50.0"]


def test_rolling_min_window_3():
    rows = _rows([5, 3, 8, 1, 4])
    result = rolling_min(rows, "val", window=3)
    mins = [r["val_rolling_min"] for r in result]
    assert mins[2] == "3.0"
    assert mins[3] == "1.0"


def test_rolling_max_window_2():
    rows = _rows([1, 5, 2, 9])
    result = rolling_max(rows, "val", window=2)
    assert [r["val_rolling_max"] for r in result] == ["1.0", "5.0", "5.0", "9.0"]


def test_custom_dest_column():
    rows = _rows([1, 2, 3])
    result = rolling_mean(rows, "val", window=2, dest="avg")
    assert "avg" in result[0]
    assert "val_rolling_mean" not in result[0]


def test_non_numeric_rows_empty():
    rows = [{"val": "abc"}, {"val": "2"}, {"val": "3"}]
    result = rolling_sum(rows, "val", window=2)
    assert result[0]["val_rolling_sum"] == ""
    assert result[1]["val_rolling_sum"] == "2.0"


def test_does_not_mutate_original():
    rows = _rows([1, 2, 3])
    original = [dict(r) for r in rows]
    rolling_mean(rows, "val", window=2)
    assert rows == original


def test_missing_column_returns_empty():
    rows = [{"other": "1"}, {"other": "2"}]
    result = rolling_sum(rows, "val", window=2)
    assert result[0]["val_rolling_sum"] == ""
