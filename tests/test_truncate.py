import pytest
from csvwrangler.truncate import truncate_column, truncate_many, truncate_all

SAMPLE = [
    {"name": "Alexander", "city": "San Francisco", "code": "XY"},
    {"name": "Jo", "city": "LA", "code": "ABCDEF"},
    {"name": "", "city": "Portland", "code": ""},
]


def test_truncate_shortens_long_value():
    result = truncate_column(SAMPLE, "name", 5)
    assert result[0]["name"] == "Alexa"


def test_truncate_leaves_short_value_unchanged():
    result = truncate_column(SAMPLE, "name", 5)
    assert result[1]["name"] == "Jo"


def test_truncate_empty_string_unchanged():
    result = truncate_column(SAMPLE, "name", 5)
    assert result[2]["name"] == ""


def test_truncate_with_suffix():
    result = truncate_column(SAMPLE, "name", 5, suffix="...")
    assert result[0]["name"] == "Al..."
    assert len(result[0]["name"]) == 5


def test_truncate_suffix_longer_than_max_len():
    result = truncate_column(SAMPLE, "name", 2, suffix="...")
    assert result[0]["name"] == "..."


def test_truncate_does_not_mutate_original():
    original = [{"name": "Alexander"}]
    truncate_column(original, "name", 3)
    assert original[0]["name"] == "Alexander"


def test_truncate_missing_column_ignored():
    result = truncate_column(SAMPLE, "nonexistent", 3)
    assert result[0]["name"] == "Alexander"


def test_truncate_negative_max_len_raises():
    with pytest.raises(ValueError):
        truncate_column(SAMPLE, "name", -1)


def test_truncate_zero_max_len():
    result = truncate_column(SAMPLE, "name", 0)
    assert result[0]["name"] == ""


def test_truncate_many_multiple_columns():
    result = truncate_many(SAMPLE, ["name", "city"], 3)
    assert result[0]["name"] == "Ale"
    assert result[0]["city"] == "San"
    assert result[0]["code"] == "XY"


def test_truncate_all_columns():
    rows = [{"a": "hello", "b": "world", "c": "!"}]
    result = truncate_all(rows, 3)
    assert result[0]["a"] == "hel"
    assert result[0]["b"] == "wor"
    assert result[0]["c"] == "!"


def test_truncate_all_empty_rows():
    assert truncate_all([], 5) == []
