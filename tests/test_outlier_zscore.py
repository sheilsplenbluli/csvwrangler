"""Additional z-score and edge-case tests for outlier.py"""
import pytest
from csvwrangler.outlier import flag_outliers, filter_outliers


def _make_rows(vals):
    return [{"v": str(x)} for x in vals]


def test_zscore_no_outlier_in_uniform_data():
    rows = _make_rows([5, 5, 5, 5, 5, 5])
    # stdev=0 so nothing should be flagged
    result = flag_outliers(rows, "v", method="zscore")
    assert all(r["_outlier"] == "0" for r in result)


def test_iqr_factor_zero_flags_many():
    rows = _make_rows([1, 2, 3, 4, 5])
    result = flag_outliers(rows, "v", method="iqr", factor=0.0)
    # with factor=0, values outside [q1,q3] are outliers
    flags = [r["_outlier"] for r in result]
    assert "1" in flags


def test_filter_outliers_zscore_keep():
    rows = _make_rows(list(range(20)) + [1000])
    result = filter_outliers(rows, "v", method="zscore", factor=2.0, keep=True)
    assert len(result) == 1
    assert result[0]["v"] == "1000"


def test_filter_outliers_removes_flag_column():
    rows = _make_rows([1, 2, 3, 100])
    result = filter_outliers(rows, "v", keep=True)
    assert all("_outlier" not in r for r in result)


def test_flag_all_non_numeric():
    rows = [{"v": "abc"}, {"v": "xyz"}, {"v": "foo"}]
    result = flag_outliers(rows, "v")
    # fewer than 2 numeric values -> empty flag
    assert all(r["_outlier"] == "" for r in result)


def test_large_dataset_performance():
    import random
    random.seed(42)
    rows = [{"v": str(random.gauss(50, 5))} for _ in range(500)]
    rows.append({"v": "9999"})
    result = flag_outliers(rows, "v", method="iqr")
    outliers = [r for r in result if r["_outlier"] == "1"]
    assert len(outliers) >= 1
