"""Edge case tests for csvwrangler/dateparse.py."""
import pytest
from csvwrangler.dateparse import extract_parts, format_date, date_diff, _parse


def test_parse_iso_datetime():
    dt = _parse("2023-06-15T10:30:00")
    assert dt is not None
    assert dt.hour == 10


def test_parse_space_datetime():
    dt = _parse("2023-06-15 10:30:00")
    assert dt is not None
    assert dt.minute == 30


def test_parse_none_input():
    assert _parse(None) is None


def test_parse_empty_string():
    assert _parse("") is None


def test_extract_empty_rows():
    result = extract_parts([], "date", ["year"])
    assert result == []


def test_extract_all_parts():
    rows = [{"date": "2023-04-15"}]
    result = extract_parts(rows, "date", ["year", "month", "day", "weekday", "quarter"])
    assert result[0]["date_quarter"] == "2"
    assert result[0]["date_weekday"] == "Saturday"


def test_format_empty_rows():
    result = format_date([], "date", "%Y")
    assert result == []


def test_diff_same_date_is_zero():
    rows = [{"a": "2023-06-15", "b": "2023-06-15"}]
    result = date_diff(rows, "a", "b")
    assert result[0]["a_minus_b"] == "0"


def test_diff_seconds_unit():
    rows = [{"a": "2023-06-15 00:01:00", "b": "2023-06-15 00:00:00"}]
    result = date_diff(rows, "a", "b", unit="seconds")
    assert result[0]["a_minus_b"] == "60"


def test_diff_both_invalid_gives_empty():
    rows = [{"a": "bad", "b": "also-bad"}]
    result = date_diff(rows, "a", "b")
    assert result[0]["a_minus_b"] == ""


def test_extract_preserves_other_columns():
    rows = [{"id": "42", "date": "2023-06-15", "name": "Alice"}]
    result = extract_parts(rows, "date", ["year"])
    assert result[0]["id"] == "42"
    assert result[0]["name"] == "Alice"


def test_format_does_not_mutate_original():
    rows = [{"date": "2023-06-15"}]
    original_val = rows[0]["date"]
    format_date(rows, "date", "%Y", dest="year")
    assert rows[0]["date"] == original_val
    assert "year" not in rows[0]
