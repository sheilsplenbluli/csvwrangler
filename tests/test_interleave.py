import pytest
from csvwrangler.interleave import interleave_rows, interleave_weighted


def _ds(rows):
    """Helper: list of dicts."""
    return rows


A = [{"x": "a1"}, {"x": "a2"}, {"x": "a3"}]
B = [{"x": "b1"}, {"x": "b2"}, {"x": "b3"}]


def test_round_robin_basic():
    result = interleave_rows([A, B])
    xs = [r["x"] for r in result]
    assert xs == ["a1", "b1", "a2", "b2", "a3", "b3"]


def test_round_robin_stops_at_shortest():
    short = [{"x": "s1"}]
    result = interleave_rows([A, short])
    assert len(result) == 2
    assert result[0]["x"] == "a1"
    assert result[1]["x"] == "s1"


def test_round_robin_empty_datasets():
    assert interleave_rows([]) == []


def test_round_robin_single_dataset():
    result = interleave_rows([A])
    assert result == A


def test_fill_pads_shorter_dataset():
    short = [{"x": "s1"}]
    result = interleave_rows([A, short], fill="")
    assert len(result) == 6  # 3 pairs
    assert result[3]["x"] == ""  # padded row


def test_fill_merges_different_fields():
    ds1 = [{"a": "1"}]
    ds2 = [{"b": "2"}]
    result = interleave_rows([ds1, ds2], fill="N/A")
    assert result[0] == {"a": "1", "b": "N/A"}
    assert result[1] == {"a": "N/A", "b": "2"}


def test_fill_preserves_field_order():
    ds1 = [{"a": "1", "b": "2"}]
    ds2 = [{"c": "3"}]
    result = interleave_rows([ds1, ds2], fill="")
    assert list(result[0].keys()) == ["a", "b", "c"]


def test_weighted_basic():
    result = interleave_weighted([A, B], weights=[2, 1])
    xs = [r["x"] for r in result]
    assert xs == ["a1", "a2", "b1"]


def test_weighted_equal_weights_same_as_round_robin():
    result = interleave_weighted([A, B], weights=[1, 1])
    xs = [r["x"] for r in result]
    assert xs == ["a1", "b1", "a2", "b2", "a3", "b3"]


def test_weighted_mismatched_lengths_raises():
    with pytest.raises(ValueError, match="same length"):
        interleave_weighted([A, B], weights=[1])


def test_weighted_empty():
    assert interleave_weighted([], weights=[]) == []
