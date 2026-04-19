from csvwrangler.merge import merge_rows, merge_summary


def test_merge_three_datasets():
    d1 = [{"a": "1"}]
    d2 = [{"a": "2"}]
    d3 = [{"a": "3"}]
    result = merge_rows([d1, d2, d3])
    assert [r["a"] for r in result] == ["1", "2", "3"]


def test_merge_preserves_column_order_first_appearance():
    d1 = [{"z": "1", "a": "2"}]
    d2 = [{"b": "3"}]
    result = merge_rows([d1, d2])
    assert list(result[0].keys()) == ["z", "a", "b"]


def test_merge_all_empty_datasets():
    result = merge_rows([[], []])
    assert result == []


def test_summary_single_dataset():
    s = merge_summary([[{"a": "1"}, {"a": "2"}]])
    assert s["dataset_0"] == 2
    assert s["total"] == 2


def test_merge_custom_fill_non_empty():
    d1 = [{"a": "1"}]
    d2 = [{"b": "2"}]
    result = merge_rows([d1, d2], fill="-")
    assert result[0]["b"] == "-"
    assert result[1]["a"] == "-"
