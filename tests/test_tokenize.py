import pytest
from csvwrangler.tokenize import (
    token_count,
    unique_token_count,
    top_tokens,
    tokenize_many,
    _tokenize,
)


def _rows():
    return [
        {"id": "1", "text": "the cat sat on the mat"},
        {"id": "2", "text": "the dog sat"},
        {"id": "3", "text": ""},
    ]


def test_tokenize_basic():
    assert _tokenize("hello world") == ["hello", "world"]


def test_tokenize_lower():
    assert _tokenize("Hello WORLD", lower=True) == ["hello", "world"]


def test_tokenize_no_lower():
    tokens = _tokenize("Hello WORLD", lower=False)
    assert "Hello" in tokens and "WORLD" in tokens


def test_token_count_adds_column():
    result = token_count(_rows(), "text")
    assert "text_token_count" in result[0]


def test_token_count_correct_value():
    result = token_count(_rows(), "text")
    assert result[0]["text_token_count"] == "6"
    assert result[1]["text_token_count"] == "3"


def test_token_count_empty_string_is_zero():
    result = token_count(_rows(), "text")
    assert result[2]["text_token_count"] == "0"


def test_token_count_custom_dest():
    result = token_count(_rows(), "text", dest="wc")
    assert "wc" in result[0]
    assert "text_token_count" not in result[0]


def test_token_count_does_not_mutate_original():
    rows = _rows()
    token_count(rows, "text")
    assert "text_token_count" not in rows[0]


def test_unique_token_count_basic():
    result = unique_token_count(_rows(), "text")
    # "the" and "sat" repeat in row 0 so unique < total
    assert int(result[0]["text_unique_tokens"]) < 6


def test_unique_token_count_all_unique():
    rows = [{"text": "one two three"}]
    result = unique_token_count(rows, "text")
    assert result[0]["text_unique_tokens"] == "3"


def test_unique_token_count_empty():
    rows = [{"text": ""}]
    result = unique_token_count(rows, "text")
    assert result[0]["text_unique_tokens"] == "0"


def test_top_tokens_returns_list():
    result = top_tokens(_rows(), "text", n=3)
    assert len(result) <= 3
    assert "token" in result[0]
    assert "count" in result[0]
    assert "percent" in result[0]


def test_top_tokens_most_common_first():
    result = top_tokens(_rows(), "text", n=1)
    # "the" appears 3 times, "sat" appears 2 times
    assert result[0]["token"] == "the"
    assert result[0]["count"] == "3"


def test_top_tokens_percent_format():
    result = top_tokens(_rows(), "text", n=5)
    for r in result:
        float(r["percent"])  # must be parseable


def test_tokenize_many_count_and_unique():
    rows = [{"a": "hello hello world", "b": "foo bar"}]
    specs = [
        {"column": "a", "mode": "count"},
        {"column": "b", "mode": "unique"},
    ]
    result = tokenize_many(rows, specs)
    assert result[0]["a_token_count"] == "3"
    assert result[0]["b_unique_tokens"] == "2"


def test_tokenize_many_default_mode_is_count():
    rows = [{"x": "one two three"}]
    result = tokenize_many(rows, [{"column": "x"}])
    assert result[0]["x_token_count"] == "3"
