import pytest
from csvwrangler.topn import top_n, bottom_n


def _rows():
    return [
        {"name": "alice", "score": "90"},
        {"name": "bob", "score": "75"},
        {"name": "carol", "score": "90"},
        {"name": "dave", "score": "60"},
        {"name": "eve", "score": "85"},
    ]


def test_top_n_basic():
    result = top_n(_rows(), "score", 2)
    names = [r["name"] for r in result]
    assert len(result) == 2
    assert all(r["score"] in ("90", "90") for r in result)
    assert set(names).issubset({"alice", "carol"})


def test_top_n_returns_sorted_desc():
    result = top_n(_rows(), "score", 3)
    scores = [float(r["score"]) for r in result]
    assert scores == sorted(scores, reverse=True)


def test_top_n_keep_ties():
    result = top_n(_rows(), "score", 1, keep_ties=True)
    # both alice and carol have 90
    assert len(result) == 2
    names = {r["name"] for r in result}
    assert names == {"alice", "carol"}


def test_top_n_zero_returns_empty():
    assert top_n(_rows(), "score", 0) == []


def test_top_n_n_exceeds_length():
    result = top_n(_rows(), "score", 100)
    assert len(result) == 5


def test_top_n_skips_non_numeric():
    rows = [
        {"name": "a", "score": "bad"},
        {"name": "b", "score": "50"},
        {"name": "c", "score": "70"},
    ]
    result = top_n(rows, "score", 2)
    assert len(result) == 2
    assert all(r["name"] in ("b", "c") for r in result)


def test_top_n_negative_n_raises():
    with pytest.raises(ValueError):
        top_n(_rows(), "score", -1)


def test_bottom_n_basic():
    result = bottom_n(_rows(), "score", 2)
    assert len(result) == 2
    scores = [float(r["score"]) for r in result]
    assert max(scores) <= 75


def test_bottom_n_sorted_asc():
    result = bottom_n(_rows(), "score", 3)
    scores = [float(r["score"]) for r in result]
    assert scores == sorted(scores)


def test_bottom_n_keep_ties():
    rows = [
        {"name": "a", "score": "10"},
        {"name": "b", "score": "10"},
        {"name": "c", "score": "20"},
    ]
    result = bottom_n(rows, "score", 1, keep_ties=True)
    assert len(result) == 2


def test_bottom_n_zero_returns_empty():
    assert bottom_n(_rows(), "score", 0) == []


def test_does_not_mutate_original():
    rows = _rows()
    original = [dict(r) for r in rows]
    top_n(rows, "score", 2)
    assert rows == original
