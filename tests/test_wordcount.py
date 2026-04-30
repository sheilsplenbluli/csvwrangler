"""Tests for csvwrangler.wordcount."""
import pytest
from csvwrangler.wordcount import word_count, char_count, wordcount_many


def _rows(*dicts):
    return list(dicts)


# ---------------------------------------------------------------------------
# word_count
# ---------------------------------------------------------------------------

def test_word_count_basic():
    rows = _rows({"text": "hello world"})
    out = word_count(rows, "text")
    assert out[0]["text_word_count"] == "2"


def test_word_count_single_word():
    rows = _rows({"text": "hello"})
    out = word_count(rows, "text")
    assert out[0]["text_word_count"] == "1"


def test_word_count_empty_string():
    rows = _rows({"text": ""})
    out = word_count(rows, "text")
    assert out[0]["text_word_count"] == "0"


def test_word_count_extra_whitespace():
    rows = _rows({"text": "  foo   bar  baz  "})
    out = word_count(rows, "text")
    assert out[0]["text_word_count"] == "3"


def test_word_count_custom_dest():
    rows = _rows({"text": "a b c"})
    out = word_count(rows, "text", dest="wc")
    assert "wc" in out[0]
    assert out[0]["wc"] == "3"


def test_word_count_custom_sep():
    rows = _rows({"csv": "a,b,c,d"})
    out = word_count(rows, "csv", sep=",")
    assert out[0]["csv_word_count"] == "4"


def test_word_count_does_not_mutate_original():
    row = {"text": "hello world"}
    word_count([row], "text")
    assert "text_word_count" not in row


# ---------------------------------------------------------------------------
# char_count
# ---------------------------------------------------------------------------

def test_char_count_basic():
    rows = _rows({"text": "hello"})
    out = char_count(rows, "text")
    assert out[0]["text_char_count"] == "5"


def test_char_count_strips_by_default():
    rows = _rows({"text": "  hi  "})
    out = char_count(rows, "text")
    assert out[0]["text_char_count"] == "2"


def test_char_count_no_strip():
    rows = _rows({"text": "  hi  "})
    out = char_count(rows, "text", strip=False)
    assert out[0]["text_char_count"] == "6"


def test_char_count_empty():
    rows = _rows({"text": ""})
    out = char_count(rows, "text")
    assert out[0]["text_char_count"] == "0"


def test_char_count_custom_dest():
    rows = _rows({"text": "abc"})
    out = char_count(rows, "text", dest="length")
    assert out[0]["length"] == "3"


# ---------------------------------------------------------------------------
# wordcount_many
# ---------------------------------------------------------------------------

def test_wordcount_many_word_and_char():
    rows = _rows({"text": "hello world"})
    specs = [
        {"column": "text", "mode": "word"},
        {"column": "text", "mode": "char"},
    ]
    out = wordcount_many(rows, specs)
    assert out[0]["text_word_count"] == "2"
    assert out[0]["text_char_count"] == "11"


def test_wordcount_many_unknown_mode_raises():
    rows = _rows({"text": "hi"})
    with pytest.raises(ValueError, match="Unknown mode"):
        wordcount_many(rows, [{"column": "text", "mode": "bytes"}])
