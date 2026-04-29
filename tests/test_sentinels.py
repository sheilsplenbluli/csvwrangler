import pytest
from csvwrangler.sentinels import replace_sentinels, sentinel_report, _DEFAULT_SENTINELS


def _rows(*dicts):
    return list(dicts)


# --- replace_sentinels ---

def test_replaces_na_with_empty():
    rows = _rows({"a": "N/A", "b": "hello"})
    result = list(replace_sentinels(rows))
    assert result[0]["a"] == ""
    assert result[0]["b"] == "hello"


def test_replaces_null_lowercase():
    rows = _rows({"x": "null"})
    result = list(replace_sentinels(rows))
    assert result[0]["x"] == ""


def test_non_sentinel_unchanged():
    rows = _rows({"col": "actual_value"})
    result = list(replace_sentinels(rows))
    assert result[0]["col"] == "actual_value"


def test_custom_replacement_string():
    rows = _rows({"a": "NA", "b": "ok"})
    result = list(replace_sentinels(rows, replacement="MISSING"))
    assert result[0]["a"] == "MISSING"
    assert result[0]["b"] == "ok"


def test_custom_sentinel_set():
    rows = _rows({"a": "UNKNOWN", "b": "N/A"})
    result = list(replace_sentinels(rows, sentinels={"UNKNOWN"}))
    assert result[0]["a"] == ""
    # N/A not in custom set, so left alone
    assert result[0]["b"] == "N/A"


def test_column_subset_only():
    rows = _rows({"a": "N/A", "b": "N/A"})
    result = list(replace_sentinels(rows, columns=["a"]))
    assert result[0]["a"] == ""
    assert result[0]["b"] == "N/A"


def test_strip_whitespace_before_compare():
    rows = _rows({"a": "  N/A  "})
    result = list(replace_sentinels(rows, strip=True))
    assert result[0]["a"] == ""


def test_no_strip_does_not_match_padded():
    rows = _rows({"a": "  N/A  "})
    result = list(replace_sentinels(rows, strip=False))
    assert result[0]["a"] == "  N/A  "


def test_does_not_mutate_original():
    original = {"a": "null"}
    rows = [original]
    list(replace_sentinels(rows))
    assert original["a"] == "null"


def test_missing_column_in_row_skipped():
    rows = _rows({"a": "hello"})
    # asking to process column "z" which doesn't exist — should not raise
    result = list(replace_sentinels(rows, columns=["z"]))
    assert result[0] == {"a": "hello"}


# --- sentinel_report ---

def test_report_counts_sentinels():
    rows = _rows({"a": "N/A"}, {"a": "null"}, {"a": "real"})
    report = sentinel_report(rows)
    assert report.get("a") == 2


def test_report_empty_when_no_sentinels():
    rows = _rows({"a": "hello"}, {"a": "world"})
    report = sentinel_report(rows)
    assert report == {}


def test_report_column_subset():
    rows = _rows({"a": "N/A", "b": "N/A"})
    report = sentinel_report(rows, columns=["a"])
    assert "a" in report
    assert "b" not in report


def test_default_sentinels_set_is_nonempty():
    assert len(_DEFAULT_SENTINELS) > 0
    assert "N/A" in _DEFAULT_SENTINELS
    assert "null" in _DEFAULT_SENTINELS
