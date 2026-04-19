import pytest
from csvwrangler.coalesce import coalesce_columns, coalesce_with_default


def _rows():
    return [
        {"a": "",  "b": "hello", "c": "world"},
        {"a": "first", "b": "second", "c": "third"},
        {"a": "",  "b": "",      "c": "only"},
        {"a": "",  "b": "",      "c": ""},
    ]


def test_picks_first_non_empty():
    result = coalesce_columns(_rows(), ["a", "b", "c"], "out")
    assert result[0]["out"] == "hello"
    assert result[1]["out"] == "first"
    assert result[2]["out"] == "only"
    assert result[3]["out"] == ""


def test_sources_kept_by_default():
    result = coalesce_columns(_rows(), ["a", "b"], "out")
    assert "a" in result[0]
    assert "b" in result[0]


def test_sources_dropped_when_requested():
    result = coalesce_columns(_rows(), ["a", "b"], "out", keep_sources=False)
    assert "a" not in result[0]
    assert "b" not in result[0]
    assert "c" in result[0]  # non-source column survives


def test_dest_same_as_source_kept():
    """When dest is one of the sources, keep_sources=False should not drop dest."""
    rows = [{"a": "", "b": "val"}]
    result = coalesce_columns(rows, ["a", "b"], "a", keep_sources=False)
    assert "a" in result[0]
    assert result[0]["a"] == "val"


def test_does_not_mutate_original():
    rows = _rows()
    original_a = rows[0]["a"]
    coalesce_columns(rows, ["a", "b", "c"], "out")
    assert rows[0]["a"] == original_a
    assert "out" not in rows[0]


def test_whitespace_only_treated_as_empty():
    rows = [{"a": "   ", "b": "real"}]
    result = coalesce_columns(rows, ["a", "b"], "out")
    assert result[0]["out"] == "real"


def test_coalesce_with_default_fills_fallback():
    rows = [{"a": "", "b": ""}]
    result = coalesce_with_default(rows, ["a", "b"], "out", default="N/A")
    assert result[0]["out"] == "N/A"


def test_coalesce_with_default_does_not_override_found_value():
    rows = [{"a": "", "b": "found"}]
    result = coalesce_with_default(rows, ["a", "b"], "out", default="N/A")
    assert result[0]["out"] == "found"


def test_empty_sources_list():
    rows = [{"a": "x"}]
    result = coalesce_columns(rows, [], "out")
    assert result[0]["out"] == ""
