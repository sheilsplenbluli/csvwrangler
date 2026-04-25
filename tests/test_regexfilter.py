"""Tests for csvwrangler.regexfilter."""
import pytest
from csvwrangler.regexfilter import regex_filter, regex_extract


ROWS = [
    {"name": "Alice", "email": "alice@example.com"},
    {"name": "Bob", "email": "bob@work.org"},
    {"name": "Charlie", "email": "charlie@example.com"},
    {"name": "Dave", "email": "dave123@gmail.com"},
    {"name": "Eve", "email": ""},
]


def test_filter_basic_match():
    result = regex_filter(ROWS, "email", r"example\.com")
    assert len(result) == 2
    names = [r["name"] for r in result]
    assert "Alice" in names
    assert "Charlie" in names


def test_filter_invert():
    result = regex_filter(ROWS, "email", r"example\.com", invert=True)
    names = [r["name"] for r in result]
    assert "Alice" not in names
    assert "Charlie" not in names
    assert "Bob" in names
    assert "Dave" in names


def test_filter_ignore_case():
    result = regex_filter(ROWS, "name", r"alice", ignore_case=True)
    assert len(result) == 1
    assert result[0]["name"] == "Alice"


def test_filter_case_sensitive_no_match():
    result = regex_filter(ROWS, "name", r"alice", ignore_case=False)
    assert len(result) == 0


def test_filter_empty_value_no_match():
    result = regex_filter(ROWS, "email", r".+")
    # Eve has empty email, should be excluded
    names = [r["name"] for r in result]
    assert "Eve" not in names


def test_filter_missing_column_treated_as_empty():
    rows = [{"name": "Alice"}, {"name": "Bob", "extra": "yes"}]
    result = regex_filter(rows, "extra", r"yes")
    assert len(result) == 1
    assert result[0]["name"] == "Bob"


def test_filter_empty_rows_returns_empty():
    assert regex_filter([], "email", r".*") == []


def test_extract_full_match():
    rows = [{"text": "order-1234"}, {"text": "ref-5678"}, {"text": "no-digits"}]
    result = regex_extract(rows, "text", r"\d+")
    assert result[0]["text_match"] == "1234"
    assert result[1]["text_match"] == "5678"
    assert result[2]["text_match"] == ""


def test_extract_capture_group():
    rows = [{"email": "alice@example.com"}, {"email": "bob@work.org"}]
    result = regex_extract(rows, "email", r"@([\w.]+)", group=1)
    assert result[0]["email_match"] == "example.com"
    assert result[1]["email_match"] == "work.org"


def test_extract_custom_dest():
    rows = [{"val": "abc123"}]
    result = regex_extract(rows, "val", r"\d+", dest="digits")
    assert "digits" in result[0]
    assert result[0]["digits"] == "123"


def test_extract_does_not_mutate_original():
    rows = [{"text": "hello world"}]
    original = dict(rows[0])
    regex_extract(rows, "text", r"hello")
    assert rows[0] == original


def test_extract_invalid_group_returns_empty():
    rows = [{"text": "hello"}]
    # pattern has no group 1
    result = regex_extract(rows, "text", r"hello", group=1)
    assert result[0]["text_match"] == ""
