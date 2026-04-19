import pytest
from csvwrangler.merge import merge_rows, merge_summary


DS1 = [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]
DS2 = [{"a": "5", "b": "6"}, {"a": "7", "b": "8"}]
DS3 = [{"a": "9", "c": "10"}]


def test_merge_two_same_schema():
    result = merge_rows([DS1, DS2])
    assert len(result) == 4
    assert result[0] == {"a": "1", "b": "2"}
    assert result[3] == {"a": "7", "b": "8"}


def test_merge_fills_missing_columns():
    result = merge_rows([DS1, DS3])
    assert "c" in result[0]
    assert result[0]["c"] == ""
    assert result[2]["b"] == ""


def test_merge_custom_fill_value():
    result = merge_rows([DS1, DS3], fill="N/A")
    assert result[0]["c"] == "N/A"


def test_merge_explicit_fieldnames():
    result = merge_rows([DS1, DS2], fieldnames=["b", "a"])
    assert list(result[0].keys()) == ["b", "a"]


def test_merge_explicit_fieldnames_drops_extra():
    result = merge_rows([DS3], fieldnames=["a"])
    assert list(result[0].keys()) == ["a"]
    assert "c" not in result[0]


def test_merge_empty_datasets_list():
    assert merge_rows([]) == []


def test_merge_one_empty_dataset():
    result = merge_rows([DS1, []])
    assert len(result) == 2


def test_merge_does_not_mutate_original():
    ds = [{"a": "1"}]
    merge_rows([ds], fill="x")
    assert ds[0] == {"a": "1"}


def test_summary_counts():
    s = merge_summary([DS1, DS2, DS3])
    assert s["dataset_0"] == 2
    assert s["dataset_1"] == 2
    assert s["dataset_2"] == 1
    assert s["total"] == 5


def test_summary_empty():
    s = merge_summary([])
    assert s["total"] == 0
