import pytest
from csvwrangler.mask import mask_column, mask_many, _mask_full, _mask_partial, _mask_regex
import re


# --- unit helpers ---

def test_mask_full_replaces_all_chars():
    assert _mask_full("hello") == "*****"


def test_mask_full_custom_char():
    assert _mask_full("abc", "#") == "###"


def test_mask_full_empty_passthrough():
    assert _mask_full("") == ""


def test_mask_partial_keeps_ends():
    assert _mask_partial("1234567890", 2, 2) == "12******90"


def test_mask_partial_no_end():
    assert _mask_partial("abcdef", 2, 0) == "ab****"


def test_mask_partial_too_short_passthrough():
    # keep_start + keep_end >= len → no masking
    assert _mask_partial("abc", 2, 2) == "abc"


def test_mask_partial_empty_passthrough():
    assert _mask_partial("", 1, 1) == ""


def test_mask_regex_replaces_match():
    pat = re.compile(r"\d+")
    assert _mask_regex("call 1800 now", pat, "###") == "call ### now"


def test_mask_regex_no_match_unchanged():
    pat = re.compile(r"\d+")
    assert _mask_regex("no digits here", pat, "###") == "no digits here"


def test_mask_regex_empty_passthrough():
    pat = re.compile(r"\d+")
    assert _mask_regex("", pat) == ""


# --- mask_column ---

def _rows():
    return [
        {"name": "Alice", "email": "alice@example.com", "phone": "0412345678"},
        {"name": "Bob",   "email": "bob@test.org",      "phone": "0498765432"},
    ]


def test_mask_column_full():
    result = mask_column(_rows(), "name", mode="full")
    assert result[0]["name"] == "*****"
    assert result[1]["name"] == "***"


def test_mask_column_partial_email():
    result = mask_column(_rows(), "email", mode="partial", keep_start=3, keep_end=4)
    assert result[0]["email"].startswith("ali")
    assert result[0]["email"].endswith(".com")
    assert "*" in result[0]["email"]


def test_mask_column_regex_phone():
    result = mask_column(_rows(), "phone", mode="regex", pattern=r"\d", replacement="X")
    assert result[0]["phone"] == "XXXXXXXXXX"


def test_mask_column_does_not_mutate_original():
    rows = _rows()
    mask_column(rows, "name", mode="full")
    assert rows[0]["name"] == "Alice"


def test_mask_column_missing_column_empty_passthrough():
    rows = [{"a": "hello"}]
    result = mask_column(rows, "b", mode="full")
    assert result[0]["b"] == ""


def test_mask_column_custom_char():
    rows = [{"ssn": "123-45-6789"}]
    result = mask_column(rows, "ssn", mode="full", char="X")
    assert result[0]["ssn"] == "XXXXXXXXXXX"


# --- mask_many ---

def test_mask_many_applies_multiple_specs():
    rows = _rows()
    specs = [
        {"column": "name", "mode": "full"},
        {"column": "phone", "mode": "partial", "keep_start": 2, "keep_end": 2},
    ]
    result = mask_many(rows, specs)
    assert result[0]["name"] == "*****"
    assert result[0]["phone"].startswith("04")
    assert result[0]["phone"].endswith("78")
    # email untouched
    assert result[0]["email"] == "alice@example.com"
