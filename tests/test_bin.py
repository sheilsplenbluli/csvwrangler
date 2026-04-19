import pytest
from csvwrangler.bin import bin_column, bin_many, _default_labels


def _rows(*values, col="score"):
    return [{col: str(v)} for v in values]


def test_default_labels_two_edges():
    assert _default_labels([10, 20]) == ["<=10", "10-20", ">20"]


def test_default_labels_no_edges():
    assert _default_labels([]) == []


def test_bin_basic():
    rows = _rows(5, 15, 25)
    result = bin_column(rows, "score", edges=[10, 20])
    bins = [r["score_bin"] for r in result]
    assert bins == ["<=10", "10-20", ">20"]


def test_bin_exact_edge_value_goes_left():
    rows = _rows(10, 10.0001)
    result = bin_column(rows, "score", edges=[10], labels=["low", "high"])
    assert result[0]["score_bin"] == "low"
    assert result[1]["score_bin"] == "high"


def test_bin_custom_labels():
    rows = _rows(1, 50, 99)
    result = bin_column(rows, "score", edges=[33, 66], labels=["low", "mid", "high"])
    bins = [r["score_bin"] for r in result]
    assert bins == ["low", "mid", "high"]


def test_bin_non_numeric_uses_default():
    rows = [{"score": "n/a"}, {"score": ""}, {"score": "10"}]
    result = bin_column(rows, "score", edges=[5, 15], labels=["lo", "mid", "hi"], default="?")
    assert result[0]["score_bin"] == "?"
    assert result[1]["score_bin"] == "?"
    assert result[2]["score_bin"] == "mid"


def test_bin_dest_column():
    rows = _rows(5)
    result = bin_column(rows, "score", edges=[10], labels=["low", "high"], dest="bucket")
    assert "bucket" in result[0]
    assert "score_bin" not in result[0]


def test_bin_does_not_mutate_original():
    rows = [{"score": "5"}]
    original = dict(rows[0])
    bin_column(rows, "score", edges=[10])
    assert rows[0] == original


def test_bin_wrong_label_count_raises():
    with pytest.raises(ValueError):
        bin_column([{"score": "1"}], "score", edges=[10], labels=["only_one"])


def test_bin_negative_values():
    rows = _rows(-5, 0, 5)
    result = bin_column(rows, "score", edges=[-1, 1], labels=["neg", "zero", "pos"])
    bins = [r["score_bin"] for r in result]
    assert bins == ["neg", "zero", "pos"]


def test_bin_many_applies_all_specs():
    rows = [{"age": "25", "salary": "55000"}]
    result = bin_many(rows, [
        {"column": "age", "edges": [30, 60], "labels": ["young", "mid", "senior"]},
        {"column": "salary", "edges": [40000, 80000], "labels": ["low", "mid", "high"]},
    ])
    assert result[0]["age_bin"] == "young"
    assert result[0]["salary_bin"] == "mid"
