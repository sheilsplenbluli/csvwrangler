import pytest
from csvwrangler.clamp import clamp_column, clamp_many


def _rows():
    return [
        {"name": "a", "score": "5"},
        {"name": "b", "score": "15"},
        {"name": "c", "score": "-3"},
        {"name": "d", "score": "10"},
        {"name": "e", "score": "n/a"},
    ]


def test_clamp_upper_only():
    result = clamp_column(_rows(), "score", high=10)
    scores = [r["score"] for r in result]
    assert scores == ["5", "10", "-3", "10", "n/a"]


def test_clamp_lower_only():
    result = clamp_column(_rows(), "score", low=0)
    scores = [r["score"] for r in result]
    assert scores == ["5", "15", "0", "10", "n/a"]


def test_clamp_both_bounds():
    result = clamp_column(_rows(), "score", low=0, high=10)
    scores = [r["score"] for r in result]
    assert scores == ["5", "10", "0", "10", "n/a"]


def test_clamp_non_numeric_passthrough():
    result = clamp_column(_rows(), "score", low=0, high=10)
    assert result[4]["score"] == "n/a"


def test_clamp_does_not_mutate_original():
    rows = _rows()
    clamp_column(rows, "score", low=0, high=10)
    assert rows[1]["score"] == "15"


def test_clamp_dest_column_keeps_original():
    result = clamp_column(_rows(), "score", low=0, high=10, dest="score_clamped")
    assert result[1]["score"] == "15"
    assert result[1]["score_clamped"] == "10"


def test_clamp_dest_column_added_to_all_rows():
    result = clamp_column(_rows(), "score", low=0, high=10, dest="score_clamped")
    for row in result:
        assert "score_clamped" in row


def test_clamp_float_value_preserved():
    rows = [{"v": "3.7"}]
    result = clamp_column(rows, "v", low=0, high=5)
    assert result[0]["v"] == "3.7"


def test_clamp_float_clamped_to_int_boundary():
    rows = [{"v": "12.5"}]
    result = clamp_column(rows, "v", high=10)
    assert result[0]["v"] == "10"


def test_clamp_invalid_bounds_raises():
    with pytest.raises(ValueError, match="low"):
        clamp_column(_rows(), "score", low=10, high=5)


def test_clamp_no_bounds_is_noop():
    result = clamp_column(_rows(), "score")
    assert [r["score"] for r in result] == ["5", "15", "-3", "10", "n/a"]


def test_clamp_many_applies_all_specs():
    rows = [
        {"a": "20", "b": "-5"},
        {"a": "3", "b": "50"},
    ]
    specs = [
        {"column": "a", "high": 10},
        {"column": "b", "low": 0},
    ]
    result = clamp_many(rows, specs)
    assert result[0]["a"] == "10"
    assert result[0]["b"] == "0"
    assert result[1]["a"] == "3"
    assert result[1]["b"] == "50"


def test_clamp_many_with_dest():
    rows = [{"x": "100"}]
    specs = [{"column": "x", "high": 50, "dest": "x_capped"}]
    result = clamp_many(rows, specs)
    assert result[0]["x"] == "100"
    assert result[0]["x_capped"] == "50"
