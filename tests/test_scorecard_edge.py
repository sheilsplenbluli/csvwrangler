"""Edge cases for scorecard."""
from csvwrangler.scorecard import score_rows, scorecard_summary


def test_non_numeric_value_with_numeric_op_scores_zero():
    rows = [{"val": "abc"}]
    rules = [{"col": "val", "op": "gt", "threshold": "10", "points": 5}]
    result = score_rows(rows, rules)
    assert result[0]["score"] == "0"


def test_non_numeric_threshold_with_numeric_op_scores_zero():
    rows = [{"val": "20"}]
    rules = [{"col": "val", "op": "gt", "threshold": "abc", "points": 5}]
    result = score_rows(rows, rules)
    assert result[0]["score"] == "0"


def test_missing_column_scores_zero():
    rows = [{"name": "Alice"}]
    rules = [{"col": "missing_col", "op": "notempty", "threshold": "", "points": 3}]
    result = score_rows(rows, rules)
    assert result[0]["score"] == "0"


def test_lt_rule():
    rows = [{"val": "5"}, {"val": "15"}]
    rules = [{"col": "val", "op": "lt", "threshold": "10", "points": 4}]
    result = score_rows(rows, rules)
    assert result[0]["score"] == "4"
    assert result[1]["score"] == "0"


def test_lte_rule():
    rows = [{"val": "10"}, {"val": "11"}]
    rules = [{"col": "val", "op": "lte", "threshold": "10", "points": 2}]
    result = score_rows(rows, rules)
    assert result[0]["score"] == "2"
    assert result[1]["score"] == "0"


def test_contains_case_insensitive():
    rows = [{"name": "ALICE"}, {"name": "bob"}]
    rules = [{"col": "name", "op": "contains", "threshold": "alice", "points": 1}]
    result = score_rows(rows, rules)
    assert result[0]["score"] == "1"
    assert result[1]["score"] == "0"


def test_empty_rows_returns_empty():
    result = score_rows([], [{"col": "x", "op": "gt", "threshold": "0", "points": 1}])
    assert result == []


def test_summary_with_no_score_column_returns_zero_count():
    rows = [{"name": "Alice"}]
    summary = scorecard_summary(rows, dest="score")
    assert summary["count"] == 0


def test_fractional_points():
    rows = [{"val": "5"}]
    rules = [{"col": "val", "op": "gt", "threshold": "0", "points": 2.5}]
    result = score_rows(rows, rules)
    assert float(result[0]["score"]) == 2.5
