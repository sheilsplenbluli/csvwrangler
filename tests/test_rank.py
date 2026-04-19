"""Tests for csvwrangler.rank."""
import pytest
from csvwrangler.rank import rank_column, rank_many


def _rows():
    return [
        {"name": "alice", "score": "90"},
        {"name": "bob", "score": "70"},
        {"name": "carol", "score": "80"},
        {"name": "dave", "score": "70"},
    ]


def test_rownum_ascending():
    result = rank_column(_rows(), "score", dest="rank", method="rownum", ascending=True)
    ranks = [r["rank"] for r in result]
    # ascending: 70, 70, 80, 90 -> bob=1, dave=2, carol=3, alice=4
    assert ranks[0] == "4"  # alice 90
    assert ranks[1] == "1"  # bob 70
    assert ranks[2] == "3"  # carol 80
    assert ranks[3] == "2"  # dave 70


def test_rownum_descending():
    result = rank_column(_rows(), "score", dest="rank", method="rownum", ascending=False)
    ranks = {r["name"]: r["rank"] for r in result}
    assert ranks["alice"] == "1"
    assert ranks["carol"] == "2"


def test_average_method_ties():
    result = rank_column(_rows(), "score", method="average", ascending=True)
    ranks = {r["name"]: r["rank"] for r in result}
    # bob and dave both 70, positions 1 and 2 -> average 1.5
    assert ranks["bob"] == "1.5"
    assert ranks["dave"] == "1.5"
    assert ranks["carol"] == "3"
    assert ranks["alice"] == "4"


def test_min_method_ties():
    result = rank_column(_rows(), "score", method="min", ascending=True)
    ranks = {r["name"]: r["rank"] for r in result}
    assert ranks["bob"] == "1"
    assert ranks["dave"] == "1"
    assert ranks["carol"] == "3"


def test_max_method_ties():
    result = rank_column(_rows(), "score", method="max", ascending=True)
    ranks = {r["name"]: r["rank"] for r in result}
    assert ranks["bob"] == "2"
    assert ranks["dave"] == "2"


def test_dense_method_ties():
    result = rank_column(_rows(), "score", method="dense", ascending=True)
    ranks = {r["name"]: r["rank"] for r in result}
    assert ranks["bob"] == "1"
    assert ranks["dave"] == "1"
    assert ranks["carol"] == "2"
    assert ranks["alice"] == "3"


def test_non_numeric_gets_empty_rank():
    rows = [{"v": "abc"}, {"v": "10"}, {"v": ""}]
    result = rank_column(rows, "v", method="rownum")
    ranks = [r["rank"] for r in result]
    assert ranks[0] == ""
    assert ranks[2] == ""
    assert ranks[1] == "1"


def test_empty_rows_returns_empty():
    assert rank_column([], "score") == []


def test_does_not_mutate_original():
    rows = [{"x": "5"}, {"x": "3"}]
    rank_column(rows, "x")
    assert "rank" not in rows[0]


def test_rank_many():
    rows = [
        {"a": "10", "b": "2"},
        {"a": "5", "b": "8"},
        {"a": "10", "b": "1"},
    ]
    specs = [
        {"column": "a", "dest": "rank_a", "method": "dense"},
        {"column": "b", "dest": "rank_b", "method": "rownum"},
    ]
    result = rank_many(rows, specs)
    assert "rank_a" in result[0]
    assert "rank_b" in result[0]
