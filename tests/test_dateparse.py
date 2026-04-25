"""Tests for csvwrangler/dateparse.py."""
import pytest
from csvwrangler.dateparse import extract_parts, format_date, date_diff


def _rows(*dicts):
    return list(dicts)


# --- extract_parts ---

def test_extract_year():
    rows = _rows({"date": "2023-06-15"})
    result = extract_parts(rows, "date", ["year"])
    assert result[0]["date_year"] == "2023"


def test_extract_month_and_day():
    rows = _rows({"date": "2023-06-15"})
    result = extract_parts(rows, "date", ["month", "day"])
    assert result[0]["date_month"] == "6"
    assert result[0]["date_day"] == "15"


def test_extract_weekday():
    rows = _rows({"date": "2024-01-01"})  # Monday
    result = extract_parts(rows, "date", ["weekday"])
    assert result[0]["date_weekday"] == "Monday"


def test_extract_quarter():
    rows = _rows({"date": "2023-04-01"})  # Q2
    result = extract_parts(rows, "date", ["quarter"])
    assert result[0]["date_quarter"] == "2"


def test_extract_invalid_date_gives_empty():
    rows = _rows({"date": "not-a-date"})
    result = extract_parts(rows, "date", ["year", "month"])
    assert result[0]["date_year"] == ""
    assert result[0]["date_month"] == ""


def test_extract_custom_prefix():
    rows = _rows({"date": "2023-06-15"})
    result = extract_parts(rows, "date", ["year"], prefix="d_")
    assert "d_year" in result[0]
    assert result[0]["d_year"] == "2023"


def test_extract_unknown_part_raises():
    rows = _rows({"date": "2023-06-15"})
    with pytest.raises(ValueError, match="Unknown date parts"):
        extract_parts(rows, "date", ["century"])


def test_extract_does_not_mutate_original():
    rows = [{"date": "2023-06-15"}]
    extract_parts(rows, "date", ["year"])
    assert "date_year" not in rows[0]


# --- format_date ---

def test_format_date_basic():
    rows = _rows({"date": "2023-06-15"})
    result = format_date(rows, "date", "%d/%m/%Y")
    assert result[0]["date"] == "15/06/2023"


def test_format_date_custom_dest():
    rows = _rows({"date": "2023-06-15"})
    result = format_date(rows, "date", "%B %Y", dest="pretty_date")
    assert result[0]["pretty_date"] == "June 2023"
    assert "date" in result[0]


def test_format_date_invalid_gives_empty():
    rows = _rows({"date": "oops"})
    result = format_date(rows, "date", "%Y")
    assert result[0]["date"] == ""


def test_format_date_slash_input():
    rows = _rows({"date": "15/06/2023"})
    result = format_date(rows, "date", "%Y-%m-%d")
    assert result[0]["date"] == "2023-06-15"


# --- date_diff ---

def test_date_diff_days():
    rows = _rows({"a": "2023-06-20", "b": "2023-06-15"})
    result = date_diff(rows, "a", "b", unit="days")
    assert result[0]["a_minus_b"] == "5"


def test_date_diff_negative():
    rows = _rows({"a": "2023-06-10", "b": "2023-06-15"})
    result = date_diff(rows, "a", "b", unit="days")
    assert result[0]["a_minus_b"] == "-5"


def test_date_diff_hours():
    rows = _rows({"a": "2023-06-15 06:00:00", "b": "2023-06-15 00:00:00"})
    result = date_diff(rows, "a", "b", unit="hours")
    assert result[0]["a_minus_b"] == "6"


def test_date_diff_invalid_unit_raises():
    rows = _rows({"a": "2023-06-15", "b": "2023-06-10"})
    with pytest.raises(ValueError):
        date_diff(rows, "a", "b", unit="weeks")


def test_date_diff_missing_date_gives_empty():
    rows = _rows({"a": "not-a-date", "b": "2023-06-10"})
    result = date_diff(rows, "a", "b")
    assert result[0]["a_minus_b"] == ""


def test_date_diff_custom_dest():
    rows = _rows({"start": "2023-01-10", "end": "2023-01-01"})
    result = date_diff(rows, "start", "end", dest="duration")
    assert "duration" in result[0]
    assert result[0]["duration"] == "9"
