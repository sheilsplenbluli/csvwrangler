"""Tests for csvwrangler/rolling.py"""
import pytest
from csvwrangler.rolling import cumulative_sum, cumulative_min, cumulative_max, cumulative_mean


def _rows(*values):
    return [{"val": str(v)} for v in values]


def test_cumsum_basic():
    rows = _rows(1, 2, 3)
    result = cumulative_sum(rows, "val")
    assert [r["val_cumsum"] for r in result] == ["1.0", "3.0", "6.0"]


def test_cumsum_custom_dest():
    rows = _rows(10, 20)
    result = cumulative_sum(rows, "val", dest="running")
    assert "running" in result[0]
    assert result[1]["running"] == "30.0"


def test_cumsum_non_numeric_empty():
    rows = [{"val": "a"}, {"val": "2"}, {"val": "b"}]
    result = cumulative_sum(rows, "val")
    assert result[0]["val_cumsum"] == ""
    assert result[1]["val_cumsum"] == "2.0"
    assert result[2]["val_cumsum"] == ""


def test_cumsum_does_not_mutate():
    rows = _rows(1, 2)
    original = [{**r} for r in rows]
    cumulative_sum(rows, "val")
    assert rows == original


def test_cummin_basic():
    rows = _rows(5, 3, 4, 1)
    result = cumulative_min(rows, "val")
    assert [r["val_cummin"] for r in result] == ["5.0", "3.0", "3.0", "1.0"]


def test_cummin_single_row():
    rows = _rows(7)
    result = cumulative_min(rows, "val")
    assert result[0]["val_cummin"] == "7.0"


def test_cummax_basic():
    rows = _rows(1, 5, 3, 9, 2)
    result = cumulative_max(rows, "val")
    assert [r["val_cummax"] for r in result] == ["1.0", "5.0", "5.0", "9.0", "9.0"]


def test_cummax_non_numeric_skipped():
    rows = [{"val": "3"}, {"val": "x"}, {"val": "5"}]
    result = cumulative_max(rows, "val")
    assert result[0]["val_cummax"] == "3.0"
    assert result[1]["val_cummax"] == ""
    assert result[2]["val_cummax"] == "5.0"


def test_cummean_basic():
    rows = _rows(2, 4, 6)
    result = cumulative_mean(rows, "val")
    means = [r["val_cummean"] for r in result]
    assert means[0] == "2.0"
    assert means[1] == "3.0"
    assert means[2] == "4.0"


def test_cummean_empty_rows():
    result = cumulative_mean([], "val")
    assert result == []


def test_cummean_custom_dest():
    rows = _rows(10, 20, 30)
    result = cumulative_mean(rows, "val", dest="avg_so_far")
    assert "avg_so_far" in result[0]
    assert result[2]["avg_so_far"] == "20.0"
