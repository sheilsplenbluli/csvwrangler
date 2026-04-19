import pytest
from csvwrangler.clip import clip_column, clip_many


ROWS = [
    {"name": "a", "score": "5"},
    {"name": "b", "score": "15"},
    {"name": "c", "score": "-3"},
    {"name": "d", "score": "100"},
    {"name": "e", "score": "n/a"},
]


def test_clip_upper():
    result = clip_column(ROWS, "score", upper=20)
    scores = [r["score"] for r in result]
    assert scores == ["5", "15", "-3", "20", "n/a"]


def test_clip_lower():
    result = clip_column(ROWS, "score", lower=0)
    scores = [r["score"] for r in result]
    assert scores == ["5", "15", "0", "100", "n/a"]


def test_clip_both():
    result = clip_column(ROWS, "score", lower=0, upper=20)
    scores = [r["score"] for r in result]
    assert scores == ["5", "15", "0", "20", "n/a"]


def test_clip_non_numeric_unchanged():
    result = clip_column(ROWS, "score", lower=0, upper=50)
    assert result[-1]["score"] == "n/a"


def test_clip_does_not_mutate_original():
    original = [{"score": "200"}]
    clip_column(original, "score", upper=100)
    assert original[0]["score"] == "200"


def test_clip_no_bounds_unchanged():
    result = clip_column(ROWS, "score")
    assert [r["score"] for r in result] == ["5", "15", "-3", "100", "n/a"]


def test_clip_invalid_bounds_raises():
    with pytest.raises(ValueError, match="lower"):
        clip_column(ROWS, "score", lower=50, upper=10)


def test_clip_float_values():
    rows = [{"v": "3.7"}, {"v": "9.9"}, {"v": "1.1"}]
    result = clip_column(rows, "v", lower=2.0, upper=8.0)
    assert result[0]["v"] == "3.7"
    assert result[1]["v"] == "8.0"
    assert result[2]["v"] == "2.0"


def test_clip_many():
    rows = [{"a": "200", "b": "-5"}]
    specs = [
        {"column": "a", "lower": None, "upper": 100},
        {"column": "b", "lower": 0, "upper": None},
    ]
    result = clip_many(rows, specs)
    assert result[0]["a"] == "100"
    assert result[0]["b"] == "0"


def test_clip_missing_column_leaves_row_intact():
    rows = [{"x": "10"}]
    result = clip_column(rows, "y", lower=0, upper=5)
    assert result[0] == {"x": "10"}
