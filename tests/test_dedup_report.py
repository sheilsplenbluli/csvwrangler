import pytest
from csvwrangler.dedup_report import duplicate_report, duplicate_summary


def _rows():
    return [
        {"name": "Alice", "city": "NY"},
        {"name": "Bob", "city": "LA"},
        {"name": "Alice", "city": "NY"},
        {"name": "Alice", "city": "NY"},
        {"name": "Bob", "city": "SF"},
    ]


def test_duplicate_report_excludes_unique_by_default():
    rows = _rows()
    result = duplicate_report(rows)
    names = [r["name"] for r in result]
    # Bob/SF appears once -> excluded
    assert all(not (r["name"] == "Bob" and r["city"] == "SF") for r in result)


def test_duplicate_report_count_column():
    rows = _rows()
    result = duplicate_report(rows)
    alice_rows = [r for r in result if r["name"] == "Alice"]
    assert all(r["_dup_count"] == "3" for r in alice_rows)


def test_duplicate_report_rank_column():
    rows = _rows()
    result = duplicate_report(rows)
    alice_rows = [r for r in result if r["name"] == "Alice"]
    ranks = [r["_dup_rank"] for r in alice_rows]
    assert ranks == ["1", "2", "3"]


def test_duplicate_report_include_unique():
    rows = _rows()
    result = duplicate_report(rows, include_unique=True)
    assert len(result) == len(rows)


def test_duplicate_report_subset_columns():
    rows = [
        {"name": "Alice", "score": "10"},
        {"name": "Alice", "score": "20"},
        {"name": "Bob", "score": "10"},
    ]
    result = duplicate_report(rows, columns=["name"])
    alice_rows = [r for r in result if r["name"] == "Alice"]
    assert len(alice_rows) == 2
    assert all(r["_dup_count"] == "2" for r in alice_rows)


def test_duplicate_report_custom_col_names():
    rows = [
        {"x": "1"},
        {"x": "1"},
    ]
    result = duplicate_report(rows, count_col="cnt", rank_col="pos")
    assert "cnt" in result[0]
    assert "pos" in result[0]
    assert "_dup_count" not in result[0]


def test_duplicate_report_empty_input():
    assert duplicate_report([]) == []


def test_duplicate_report_does_not_mutate_original():
    rows = [{"a": "1"}, {"a": "1"}]
    original_keys = set(rows[0].keys())
    duplicate_report(rows)
    assert set(rows[0].keys()) == original_keys


def test_summary_basic():
    rows = _rows()
    s = duplicate_summary(rows)
    assert s["total_rows"] == 5
    assert s["unique_rows"] == 1   # Bob/SF
    assert s["duplicate_groups"] == 2  # Alice/NY and Bob/LA
    assert s["duplicate_rows"] == 4


def test_summary_no_duplicates():
    rows = [{"a": "1"}, {"a": "2"}, {"a": "3"}]
    s = duplicate_summary(rows)
    assert s["duplicate_groups"] == 0
    assert s["duplicate_rows"] == 0
    assert s["unique_rows"] == 3
