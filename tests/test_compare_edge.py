"""Edge-case tests for csvwrangler.compare."""
from csvwrangler.compare import compare_columns, compare_many


def test_empty_rows_returns_empty():
    result = compare_columns([], "a", "b", mode="diff")
    assert result == []


def test_missing_column_treated_as_empty():
    rows = [{"a": "5"}]
    result = compare_columns(rows, "a", "b", mode="diff")
    # b is missing -> treated as empty -> non-numeric -> empty diff
    assert result[0]["_cmp"] == ""


def test_ratio_non_numeric_empty():
    rows = [{"a": "abc", "b": "xyz"}]
    result = compare_columns(rows, "a", "b", mode="ratio")
    assert result[0]["_cmp"] == ""


def test_eq_whitespace_stripped():
    rows = [{"a": "  yes  ", "b": "YES"}]
    result = compare_columns(rows, "a", "b", mode="eq")
    assert result[0]["_cmp"] == "1"


def test_gt_non_numeric_is_zero():
    rows = [{"a": "foo", "b": "bar"}]
    result = compare_columns(rows, "a", "b", mode="gt")
    assert result[0]["_cmp"] == "0"


def test_compare_many_default_dest_overwritten_each_time():
    # If two specs share the same dest, second spec overwrites first
    rows = [{"a": "10", "b": "2"}]
    specs = [
        {"col_a": "a", "col_b": "b", "dest": "out", "mode": "diff"},
        {"col_a": "a", "col_b": "b", "dest": "out", "mode": "eq"},
    ]
    result = compare_many(rows, specs)
    # eq result: 10 != 2 -> "0"
    assert result[0]["out"] == "0"


def test_dest_column_added_to_output():
    rows = [{"x": "1", "y": "2"}]
    result = compare_columns(rows, "x", "y", dest="result", mode="lt")
    assert "result" in result[0]
    assert result[0]["result"] == "1"
