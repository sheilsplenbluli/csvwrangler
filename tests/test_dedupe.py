import pytest
from csvwrangler.dedupe import dedupe_rows, count_duplicates


ROWS = [
    {"name": "Alice", "city": "NY"},
    {"name": "Bob",   "city": "LA"},
    {"name": "Alice", "city": "NY"},
    {"name": "Alice", "city": "SF"},
]


def test_dedupe_all_columns_keep_first():
    result = dedupe_rows(ROWS)
    assert len(result) == 3
    assert result[0] == {"name": "Alice", "city": "NY"}
    assert result[1] == {"name": "Bob",   "city": "LA"}
    assert result[2] == {"name": "Alice", "city": "SF"}


def test_dedupe_subset_columns():
    result = dedupe_rows(ROWS, columns=["name"])
    assert len(result) == 2
    assert result[0]["name"] == "Alice"
    assert result[1]["name"] == "Bob"


def test_dedupe_keep_last():
    result = dedupe_rows(ROWS, columns=["name"], keep="last")
    assert len(result) == 2
    alice = next(r for r in result if r["name"] == "Alice")
    assert alice["city"] == "SF"


def test_dedupe_no_duplicates():
    rows = [{"a": "1"}, {"a": "2"}, {"a": "3"}]
    assert dedupe_rows(rows) == rows


def test_dedupe_all_same():
    rows = [{"a": "x"}, {"a": "x"}, {"a": "x"}]
    result = dedupe_rows(rows)
    assert result == [{"a": "x"}]


def test_dedupe_empty():
    assert dedupe_rows([]) == []


def test_invalid_keep():
    with pytest.raises(ValueError, match="keep must be"):
        dedupe_rows(ROWS, keep="middle")


def test_count_duplicates():
    assert count_duplicates(ROWS) == 1


def test_count_duplicates_subset():
    assert count_duplicates(ROWS, columns=["name"]) == 2


def test_count_duplicates_none():
    rows = [{"a": "1"}, {"a": "2"}]
    assert count_duplicates(rows) == 0
