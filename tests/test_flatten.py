import pytest
from csvwrangler.flatten import flatten_column, flatten_many


def _rows(*dicts):
    return [dict(d) for d in dicts]


def test_basic_split():
    rows = _rows({"name": "alice", "tags": "a|b|c"})
    result = flatten_column(rows, "tags")
    assert len(result) == 3
    assert [r["tags"] for r in result] == ["a", "b", "c"]
    assert all(r["name"] == "alice" for r in result)


def test_single_value_passthrough():
    rows = _rows({"name": "bob", "tags": "only"})
    result = flatten_column(rows, "tags")
    assert result == [{"name": "bob", "tags": "only"}]


def test_empty_value_passthrough():
    rows = _rows({"name": "carol", "tags": ""})
    result = flatten_column(rows, "tags")
    assert result == [{"name": "carol", "tags": ""}]


def test_strip_whitespace():
    rows = _rows({"x": "1", "v": " a | b "})
    result = flatten_column(rows, "v", strip=True)
    assert [r["v"] for r in result] == ["a", "b"]


def test_no_strip():
    rows = _rows({"x": "1", "v": " a | b "})
    result = flatten_column(rows, "v", strip=False)
    assert [r["v"] for r in result] == [" a ", " b "]


def test_custom_delimiter():
    rows = _rows({"col": "x,y,z"})
    result = flatten_column(rows, "col", delimiter=",")
    assert [r["col"] for r in result] == ["x", "y", "z"]


def test_does_not_mutate_original():
    original = {"a": "1", "tags": "x|y"}
    rows = [original]
    flatten_column(rows, "tags")
    assert original["tags"] == "x|y"


def test_empty_input():
    assert flatten_column([], "col") == []


def test_missing_column_passthrough():
    rows = _rows({"name": "dave"})
    result = flatten_column(rows, "tags")
    assert result == [{"name": "dave"}]


def test_flatten_many_two_columns():
    rows = _rows({"a": "1|2", "b": "x|y", "c": "z"})
    result = flatten_many(rows, ["a", "b"])
    # 2 splits on a -> 2 rows, then 2 splits on b each -> 4 rows
    assert len(result) == 4
    a_vals = [r["a"] for r in result]
    assert a_vals.count("1") == 2
    assert a_vals.count("2") == 2


def test_flatten_many_empty_columns_list():
    rows = _rows({"a": "1|2"})
    result = flatten_many(rows, [])
    assert result == rows
