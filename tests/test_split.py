import pytest
from csvwrangler.split import split_by_column, split_by_row_count, iter_chunks


DEFAULT_ROWS = [
    {"dept": "eng", "name": "Alice"},
    {"dept": "hr", "name": "Bob"},
    {"dept": "eng", "name": "Carol"},
    {"dept": "hr", "name": "Dave"},
    {"dept": "finance", "name": "Eve"},
]


def test_split_by_column_keys():
    result = split_by_column(DEFAULT_ROWS, "dept")
    assert set(result.keys()) == {"eng", "hr", "finance"}


def test_split_by_column_counts():
    result = split_by_column(DEFAULT_ROWS, "dept")
    assert len(result["eng"]) == 2
    assert len(result["hr"]) == 2
    assert len(result["finance"]) == 1


def test_split_by_column_preserves_rows():
    result = split_by_column(DEFAULT_ROWS, "dept")
    assert result["eng"][0]["name"] == "Alice"
    assert result["eng"][1]["name"] == "Carol"


def test_split_by_column_missing_column_uses_empty_key():
    rows = [{"x": "1"}, {"dept": "eng", "x": "2"}]
    result = split_by_column(rows, "dept")
    assert "" in result
    assert len(result[""] ) == 1


def test_split_by_column_empty_rows():
    assert split_by_column([], "dept") == {}


def test_split_by_row_count_basic():
    rows = [{"n": str(i)} for i in range(10)]
    chunks = split_by_row_count(rows, 3)
    assert len(chunks) == 4
    assert len(chunks[0]) == 3
    assert len(chunks[-1]) == 1


def test_split_by_row_count_exact_multiple():
    rows = [{"n": str(i)} for i in range(6)]
    chunks = split_by_row_count(rows, 2)
    assert len(chunks) == 3


def test_split_by_row_count_invalid_raises():
    with pytest.raises(ValueError):
        split_by_row_count([], 0)


def test_iter_chunks_yields_same_as_list():
    rows = [{"n": str(i)} for i in range(7)]
    from_iter = list(iter_chunks(rows, 3))
    from_list = split_by_row_count(rows, 3)
    assert from_iter == from_list


def test_iter_chunks_invalid_raises():
    with pytest.raises(ValueError):
        list(iter_chunks([], -1))
