"""Tests for csvwrangler.percentile."""

import pytest
from csvwrangler.percentile import percentile_rank, quantile_bucket, percentile_many


def _rows():
    return [
        {"name": "a", "score": "10"},
        {"name": "b", "score": "20"},
        {"name": "c", "score": "30"},
        {"name": "d", "score": "40"},
    ]


def test_percentile_rank_adds_column():
    rows = _rows()
    result = percentile_rank(rows, "score")
    assert "score_pct_rank" in result[0]


def test_percentile_rank_min_is_25():
    rows = _rows()
    result = percentile_rank(rows, "score")
    assert float(result[0]["score_pct_rank"]) == pytest.approx(25.0)


def test_percentile_rank_max_is_100():
    rows = _rows()
    result = percentile_rank(rows, "score")
    assert float(result[-1]["score_pct_rank"]) == pytest.approx(100.0)


def test_percentile_rank_custom_dest():
    rows = _rows()
    result = percentile_rank(rows, "score", dest="pct")
    assert "pct" in result[0]
    assert "score_pct_rank" not in result[0]


def test_percentile_rank_non_numeric_empty():
    rows = [{"score": "abc"}, {"score": "10"}]
    result = percentile_rank(rows, "score")
    assert result[0]["score_pct_rank"] == ""


def test_percentile_rank_does_not_mutate():
    rows = _rows()
    original = [dict(r) for r in rows]
    percentile_rank(rows, "score")
    assert rows == original


def test_quantile_bucket_q4_assigns_1_to_4():
    rows = _rows()
    result = quantile_bucket(rows, "score", q=4)
    buckets = [int(r["score_q4"]) for r in result]
    assert set(buckets) == {1, 2, 3, 4}


def test_quantile_bucket_q2_splits_half():
    rows = _rows()
    result = quantile_bucket(rows, "score", q=2)
    buckets = [int(r["score_q2"]) for r in result]
    assert buckets[:2] == [1, 1]
    assert buckets[2:] == [2, 2]


def test_quantile_bucket_custom_dest():
    rows = _rows()
    result = quantile_bucket(rows, "score", q=4, dest="quartile")
    assert "quartile" in result[0]


def test_quantile_bucket_non_numeric_empty():
    rows = [{"score": "bad"}, {"score": "10"}]
    result = quantile_bucket(rows, "score", q=4)
    assert result[0]["score_q4"] == ""


def test_quantile_bucket_invalid_q_raises():
    with pytest.raises(ValueError):
        quantile_bucket(_rows(), "score", q=0)


def test_percentile_many_rank_then_quantile():
    rows = _rows()
    specs = [
        {"mode": "rank", "col": "score"},
        {"mode": "quantile", "col": "score", "q": 2},
    ]
    result = percentile_many(rows, specs)
    assert "score_pct_rank" in result[0]
    assert "score_q2" in result[0]


def test_percentile_many_unknown_mode_raises():
    with pytest.raises(ValueError, match="Unknown mode"):
        percentile_many(_rows(), [{"mode": "bogus", "col": "score"}])
