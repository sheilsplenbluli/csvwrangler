"""Tests for csvwrangler.regex_replace."""

import pytest
from csvwrangler.regex_replace import regex_replace, regex_replace_many


def _rows():
    return [
        {"name": "Alice Smith", "email": "alice@example.com"},
        {"name": "Bob Jones", "email": "bob@test.org"},
        {"name": "carol white", "email": "carol@example.com"},
    ]


def test_basic_replace():
    rows = regex_replace(_rows(), "name", r"\s+", "_")
    assert rows[0]["name"] == "Alice_Smith"
    assert rows[1]["name"] == "Bob_Jones"


def test_replace_writes_to_dest_column():
    rows = regex_replace(_rows(), "name", r"\s+", "-", dest="slug")
    assert rows[0]["slug"] == "Alice-Smith"
    assert rows[0]["name"] == "Alice Smith"  # original unchanged


def test_replace_ignore_case():
    rows = regex_replace(_rows(), "name", r"alice", "ALICE", ignore_case=True)
    assert rows[0]["name"] == "ALICE Smith"
    assert rows[1]["name"] == "Bob Jones"  # unaffected


def test_replace_case_sensitive_no_match():
    rows = regex_replace(_rows(), "name", r"alice", "X", ignore_case=False)
    assert rows[0]["name"] == "Alice Smith"  # capital A, no match


def test_replace_count_limits_substitutions():
    data = [{"val": "aaa"}]
    rows = regex_replace(data, "val", r"a", "b", count=2)
    assert rows[0]["val"] == "bba"


def test_replace_backreference():
    data = [{"phone": "1234567890"}]
    rows = regex_replace(data, "phone", r"(\d{3})(\d{3})(\d{4})", r"(\1) \2-\3")
    assert rows[0]["phone"] == "(123) 456-7890"


def test_replace_missing_column_uses_empty():
    data = [{"a": "hello"}]
    rows = regex_replace(data, "missing", r"x", "y", dest="out")
    assert rows[0]["out"] == ""


def test_does_not_mutate_original():
    original = [{"name": "Alice Smith"}]
    regex_replace(original, "name", r"\s", "_")
    assert original[0]["name"] == "Alice Smith"


def test_empty_rows_returns_empty():
    assert regex_replace([], "name", r"a", "b") == []


def test_regex_replace_many_applies_in_order():
    data = [{"text": "hello world"}]
    specs = [
        {"column": "text", "pattern": r"hello", "replacement": "hi"},
        {"column": "text", "pattern": r"world", "replacement": "earth"},
    ]
    rows = regex_replace_many(data, specs)
    assert rows[0]["text"] == "hi earth"


def test_regex_replace_many_with_dest():
    data = [{"city": "New York"}]
    specs = [{"column": "city", "pattern": r"\s", "replacement": "-", "dest": "city_slug"}]
    rows = regex_replace_many(data, specs)
    assert rows[0]["city_slug"] == "New-York"
    assert rows[0]["city"] == "New York"


def test_regex_replace_many_empty_specs():
    data = [{"x": "unchanged"}]
    rows = regex_replace_many(data, [])
    assert rows[0]["x"] == "unchanged"
