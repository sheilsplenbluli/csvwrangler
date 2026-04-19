import pytest
from csvwrangler.diff import diff_rows, diff_summary

LEFT = [
    {"id": "1", "name": "Alice", "score": "10"},
    {"id": "2", "name": "Bob", "score": "20"},
    {"id": "3", "name": "Carol", "score": "30"},
]

RIGHT = [
    {"id": "1", "name": "Alice", "score": "10"},
    {"id": "2", "name": "Bob", "score": "99"},
    {"id": "4", "name": "Dave", "score": "40"},
]


def test_removed_row():
    result = diff_rows(LEFT, RIGHT, ["id"])
    removed = [r for r in result if r["_diff"] == "removed"]
    assert len(removed) == 1
    assert removed[0]["id"] == "3"


def test_added_row():
    result = diff_rows(LEFT, RIGHT, ["id"])
    added = [r for r in result if r["_diff"] == "added"]
    assert len(added) == 1
    assert added[0]["id"] == "4"


def test_modified_row():
    result = diff_rows(LEFT, RIGHT, ["id"])
    modified = [r for r in result if r["_diff"] == "modified"]
    assert len(modified) == 1
    assert modified[0]["id"] == "2"
    assert modified[0]["score"] == "99"


def test_unchanged_row_omitted():
    result = diff_rows(LEFT, RIGHT, ["id"])
    ids = [r["id"] for r in result]
    assert "1" not in ids


def test_no_changes():
    result = diff_rows(LEFT, LEFT, ["id"])
    assert result == []


def test_all_added():
    result = diff_rows([], RIGHT, ["id"])
    assert all(r["_diff"] == "added" for r in result)
    assert len(result) == len(RIGHT)


def test_all_removed():
    result = diff_rows(LEFT, [], ["id"])
    assert all(r["_diff"] == "removed" for r in result)


def test_composite_key():
    left = [{"a": "1", "b": "x", "val": "old"}]
    right = [{"a": "1", "b": "x", "val": "new"}]
    result = diff_rows(left, right, ["a", "b"])
    assert result[0]["_diff"] == "modified"


def test_summary_counts():
    result = diff_rows(LEFT, RIGHT, ["id"])
    summary = diff_summary(result)
    assert summary["added"] == 1
    assert summary["removed"] == 1
    assert summary["modified"] == 1


def test_summary_empty_diff():
    summary = diff_summary([])
    assert summary == {"added": 0, "removed": 0, "modified": 0}
