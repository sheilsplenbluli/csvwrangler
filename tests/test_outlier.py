"""Tests for csvwrangler/outlier.py"""
import pytest
from csvwrangler.outlier import flag_outliers, filter_outliers

ROWS = [
    {"name": "a", "val": "10"},
    {"name": "b", "val": "12"},
    {"name": "c", "val": "11"},
    {"name": "d", "val": "13"},
    {"name": "e", "val": "200"},  # outlier
]


def test_flag_outliers_iqr_marks_outlier():
    result = flag_outliers(ROWS, "val", method="iqr")
    flags = {r["name"]: r["_outlier"] for r in result}
    assert flags["e"] == "1"
    assert all(flags[k] == "0" for k in "abcd")


def test_flag_outliers_custom_flag_column():
    result = flag_outliers(ROWS, "val", flag_column="is_out")
    assert "is_out" in result[0]
    assert "_outlier" not in result[0]


def test_flag_outliers_zscore():
    result = flag_outliers(ROWS, "val", method="zscore", factor=2.0)
    flags = {r["name"]: r["_outlier"] for r in result}
    assert flags["e"] == "1"


def test_flag_outliers_non_numeric_rows_not_flagged():
    rows = [{"val": "abc"}, {"val": "10"}, {"val": "12"}]
    result = flag_outliers(rows, "val")
    assert result[0]["_outlier"] == "0"


def test_flag_outliers_too_few_values_returns_empty_flag():
    rows = [{"val": "5"}]
    result = flag_outliers(rows, "val")
    assert result[0]["_outlier"] == ""


def test_flag_outliers_does_not_mutate_original():
    original = [{"val": "10"}, {"val": "200"}]
    flag_outliers(original, "val")
    assert "_outlier" not in original[0]


def test_filter_outliers_keep_true():
    result = filter_outliers(ROWS, "val", keep=True)
    assert len(result) == 1
    assert result[0]["name"] == "e"
    assert "_outlier" not in result[0]


def test_filter_outliers_keep_false():
    result = filter_outliers(ROWS, "val", keep=False)
    names = [r["name"] for r in result]
    assert "e" not in names
    assert len(result) == 4


def test_filter_outliers_no_outliers():
    rows = [{"v": str(i)} for i in range(10)]
    result = filter_outliers(rows, "v", keep=True)
    assert result == []
