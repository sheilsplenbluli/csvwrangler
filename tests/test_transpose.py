import pytest
from csvwrangler.transpose import transpose_rows, pivot_transpose


def _rows():
    return [
        {"name": "Alice", "age": "30", "city": "NY"},
        {"name": "Bob",   "age": "25", "city": "LA"},
        {"name": "Carol", "age": "35", "city": "SF"},
    ]


def test_transpose_row_count():
    result = transpose_rows(_rows())
    # one output row per original column
    assert len(result) == 3


def test_transpose_column_count():
    result = transpose_rows(_rows())
    # header_col + one col per original row
    assert set(result[0].keys()) == {"field", "row_0", "row_1", "row_2"}


def test_transpose_field_column_contains_original_headers():
    result = transpose_rows(_rows())
    fields = [r["field"] for r in result]
    assert fields == ["name", "age", "city"]


def test_transpose_values_correct():
    result = transpose_rows(_rows())
    name_row = next(r for r in result if r["field"] == "name")
    assert name_row["row_0"] == "Alice"
    assert name_row["row_1"] == "Bob"
    assert name_row["row_2"] == "Carol"


def test_transpose_custom_header_col():
    result = transpose_rows(_rows(), header_col="column")
    assert "column" in result[0]
    assert "field" not in result[0]


def test_transpose_empty_returns_empty():
    assert transpose_rows([]) == []


def test_pivot_transpose_basic():
    rows = [
        {"key": "color", "value": "red"},
        {"key": "size",  "value": "large"},
    ]
    result = pivot_transpose(rows, key_col="key", value_col="value")
    assert len(result) == 1
    assert result[0]["color"] == "red"
    assert result[0]["size"] == "large"


def test_pivot_transpose_last_value_wins():
    rows = [
        {"k": "x", "v": "1"},
        {"k": "x", "v": "2"},
    ]
    result = pivot_transpose(rows, key_col="k", value_col="v")
    assert result[0]["x"] == "2"


def test_pivot_transpose_empty_returns_empty():
    assert pivot_transpose([], key_col="k", value_col="v") == []


def test_pivot_transpose_skips_empty_key():
    rows = [
        {"k": "",    "v": "ignored"},
        {"k": "foo", "v": "bar"},
    ]
    result = pivot_transpose(rows, key_col="k", value_col="v")
    assert "" not in result[0]
    assert result[0]["foo"] == "bar"
