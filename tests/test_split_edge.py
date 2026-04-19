from csvwrangler.split import split_by_column, split_by_row_count


def test_single_row_single_chunk():
    rows = [{"a": "1"}]
    chunks = split_by_row_count(rows, 10)
    assert len(chunks) == 1
    assert chunks[0] == rows


def test_split_does_not_mutate_original():
    rows = [{"dept": "eng", "val": "x"}, {"dept": "hr", "val": "y"}]
    original = [dict(r) for r in rows]
    split_by_column(rows, "dept")
    assert rows == original


def test_chunk_does_not_mutate_original():
    rows = [{"n": str(i)} for i in range(5)]
    original = [dict(r) for r in rows]
    split_by_row_count(rows, 2)
    assert rows == original


def test_all_same_value_one_group():
    rows = [{"dept": "eng", "n": str(i)} for i in range(5)]
    result = split_by_column(rows, "dept")
    assert list(result.keys()) == ["eng"]
    assert len(result["eng"]) == 5


def test_chunk_size_one():
    rows = [{"n": str(i)} for i in range(4)]
    chunks = split_by_row_count(rows, 1)
    assert len(chunks) == 4
    for i, chunk in enumerate(chunks):
        assert chunk[0]["n"] == str(i)


def test_split_preserves_all_fields():
    rows = [
        {"dept": "eng", "name": "Alice", "age": "30"},
        {"dept": "hr", "name": "Bob", "age": "25"},
    ]
    result = split_by_column(rows, "dept")
    assert result["eng"][0] == {"dept": "eng", "name": "Alice", "age": "30"}
