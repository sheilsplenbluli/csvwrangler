import pytest
from csvwrangler.scorecard import score_rows, scorecard_summary


def _rows():
    return [
        {"name": "Alice", "age": "30", "city": "London"},
        {"name": "Bob", "age": "17", "city": "Paris"},
        {"name": "Carol", "age": "45", "city": "London"},
        {"name": "", "age": "", "city": ""},
    ]


def test_score_column_added():
    rows = _rows()
    result = score_rows(rows, [])
    assert "score" in result[0]


def test_gt_rule_awards_points():
    rules = [{"col": "age", "op": "gt", "threshold": "18", "points": 10}]
    result = score_rows(_rows(), rules)
    assert result[0]["score"] == "10"   # Alice 30 > 18
    assert result[1]["score"] == "0"    # Bob 17 not > 18
    assert result[2]["score"] == "10"   # Carol 45 > 18


def test_gte_rule():
    rules = [{"col": "age", "op": "gte", "threshold": "30", "points": 5}]
    result = score_rows(_rows(), rules)
    assert result[0]["score"] == "5"    # Alice 30 >= 30
    assert result[1]["score"] == "0"    # Bob 17
    assert result[2]["score"] == "5"    # Carol 45


def test_eq_rule():
    rules = [{"col": "city", "op": "eq", "threshold": "London", "points": 3}]
    result = score_rows(_rows(), rules)
    assert result[0]["score"] == "3"
    assert result[1]["score"] == "0"
    assert result[2]["score"] == "3"


def test_contains_rule():
    rules = [{"col": "name", "op": "contains", "threshold": "li", "points": 2}]
    result = score_rows(_rows(), rules)
    assert result[0]["score"] == "2"   # Alice contains 'li'
    assert result[1]["score"] == "0"


def test_notempty_rule():
    rules = [{"col": "name", "op": "notempty", "threshold": "", "points": 1}]
    result = score_rows(_rows(), rules)
    assert result[0]["score"] == "1"
    assert result[3]["score"] == "0"   # empty name row


def test_multiple_rules_accumulate():
    rules = [
        {"col": "age", "op": "gt", "threshold": "18", "points": 10},
        {"col": "city", "op": "eq", "threshold": "London", "points": 5},
    ]
    result = score_rows(_rows(), rules)
    assert result[0]["score"] == "15"  # Alice: 10 + 5
    assert result[1]["score"] == "0"   # Bob: neither
    assert result[2]["score"] == "15"  # Carol: 10 + 5


def test_custom_dest_column():
    result = score_rows(_rows(), [], dest="total_score")
    assert "total_score" in result[0]
    assert "score" not in result[0]


def test_default_score_applied():
    result = score_rows(_rows(), [], default=5.0)
    assert result[0]["score"] == "5"


def test_does_not_mutate_original():
    rows = _rows()
    original = [dict(r) for r in rows]
    score_rows(rows, [{"col": "age", "op": "gt", "threshold": "18", "points": 1}])
    assert rows == original


def test_summary_basic():
    rules = [{"col": "age", "op": "gt", "threshold": "18", "points": 10}]
    scored = score_rows(_rows()[:3], rules)
    summary = scorecard_summary(scored)
    assert summary["count"] == 3
    assert summary["min"] == 0.0
    assert summary["max"] == 10.0


def test_summary_empty_rows():
    summary = scorecard_summary([])
    assert summary["count"] == 0
    assert summary["mean"] is None
