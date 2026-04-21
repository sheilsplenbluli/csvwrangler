"""Tests for csvwrangler.stringify."""

import pytest
from csvwrangler.stringify import stringify_column, stringify_many


def _rows():
    return [
        {"name": "alice", "score": "0.85", "amount": "1234567"},
        {"name": "bob", "score": "0.5", "amount": "999"},
        {"name": "carol", "score": "", "amount": "42000"},
    ]


def test_prefix_and_suffix():
    rows = stringify_column(_rows(), "score", prefix="[", suffix="]")
    assert rows[0]["score"] == "[0.85]"
    assert rows[1]["score"] == "[0.5]"


def test_empty_value_passthrough():
    rows = stringify_column(_rows(), "score", prefix="$")
    assert rows[2]["score"] == ""


def test_decimals_rounds_value():
    rows = stringify_column(_rows(), "score", decimals=1)
    assert rows[0]["score"] == "0.8"
    assert rows[1]["score"] == "0.5"


def test_comma_format_large_integer():
    rows = stringify_column(_rows(), "amount", fmt="comma")
    assert rows[0]["amount"] == "1,234,567"
    assert rows[1]["amount"] == "999"


def test_comma_format_with_decimals():
    rows = stringify_column(_rows(), "amount", fmt="comma", decimals=2)
    assert rows[0]["amount"] == "1,234,567.00"


def test_percent_format():
    rows = stringify_column(_rows(), "score", fmt="percent", decimals=0)
    assert rows[0]["score"] == "85%"
    assert rows[1]["score"] == "50%"


def test_scientific_format():
    rows = stringify_column(_rows(), "amount", fmt="scientific", decimals=2)
    assert rows[0]["amount"] == "1.23e+06"


def test_dest_column_leaves_original():
    rows = stringify_column(_rows(), "score", prefix="~", dest="score_fmt")
    assert rows[0]["score"] == "0.85"
    assert rows[0]["score_fmt"] == "~0.85"


def test_does_not_mutate_original():
    original = _rows()
    stringify_column(original, "score", prefix="$")
    assert original[0]["score"] == "0.85"


def test_non_numeric_passthrough_for_comma():
    rows = [{"val": "hello"}]
    result = stringify_column(rows, "val", fmt="comma")
    assert result[0]["val"] == "hello"


def test_stringify_many_applies_multiple_specs():
    specs = [
        {"column": "score", "fmt": "percent", "decimals": 0},
        {"column": "amount", "fmt": "comma"},
    ]
    rows = stringify_many(_rows(), specs)
    assert rows[0]["score"] == "85%"
    assert rows[0]["amount"] == "1,234,567"


def test_stringify_many_empty_specs_unchanged():
    original = _rows()
    result = stringify_many(original, [])
    assert result[0]["score"] == "0.85"


def test_suffix_only():
    rows = stringify_column(_rows(), "score", suffix=" pts")
    assert rows[0]["score"] == "0.85 pts"
