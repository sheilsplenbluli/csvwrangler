"""Tests for csvwrangler.zscore."""
import math
import pytest
from csvwrangler.zscore import zscore_column, zscore_many


def _rows():
    return [
        {"name": "a", "val": "10"},
        {"name": "b", "val": "20"},
        {"name": "c", "val": "30"},
    ]


def test_zscore_adds_dest_column():
    result = zscore_column(_rows(), "val")
    assert "val_zscore" in result[0]


def test_zscore_mean_row_is_zero():
    result = zscore_column(_rows(), "val")
    # middle value (20) is the mean
    assert float(result[1]["val_zscore"]) == pytest.approx(0.0, abs=1e-6)


def test_zscore_symmetric():
    result = zscore_column(_rows(), "val")
    z0 = float(result[0]["val_zscore"])
    z2 = float(result[2]["val_zscore"])
    assert z0 == pytest.approx(-z2, abs=1e-6)


def test_zscore_custom_dest():
    result = zscore_column(_rows(), "val", dest="z")
    assert "z" in result[0]
    assert "val_zscore" not in result[0]


def test_zscore_non_numeric_becomes_empty():
    rows = [{"val": "10"}, {"val": "oops"}, {"val": "30"}]
    result = zscore_column(rows, "val")
    assert result[1]["val_zscore"] == ""


def test_zscore_does_not_mutate_original():
    rows = _rows()
    zscore_column(rows, "val")
    assert "val_zscore" not in rows[0]


def test_zscore_single_row_returns_empty():
    rows = [{"val": "5"}]
    result = zscore_column(rows, "val")
    assert result[0]["val_zscore"] == ""


def test_zscore_decimals_respected():
    result = zscore_column(_rows(), "val", decimals=2)
    z = str(result[0]["val_zscore"])
    # should have at most 2 decimal places
    if "." in z:
        assert len(z.split(".")[1]) <= 2


def test_zscore_many_applies_all_specs():
    rows = [
        {"a": "1", "b": "100"},
        {"a": "2", "b": "200"},
        {"a": "3", "b": "300"},
    ]
    specs = [{"col": "a"}, {"col": "b", "dest": "b_z", "decimals": 2}]
    result = zscore_many(rows, specs)
    assert "a_zscore" in result[0]
    assert "b_z" in result[0]


def test_zscore_uniform_values_all_zero():
    rows = [{"val": "7"}, {"val": "7"}, {"val": "7"}]
    result = zscore_column(rows, "val")
    for r in result:
        assert r["val_zscore"] == 0.0
