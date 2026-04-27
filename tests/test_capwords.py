"""Tests for csvwrangler/capwords.py."""
import pytest
from csvwrangler.capwords import capwords_column, capwords_many, _cap_sentence


def _rows():
    return [
        {"name": "alice smith", "city": "new york"},
        {"name": "BOB JONES", "city": "LOS ANGELES"},
        {"name": "charlie", "city": ""},
        {"name": "", "city": "boston"},
    ]


def test_title_mode_basic():
    result = capwords_column(_rows(), "name", mode="title")
    assert result[0]["name"] == "Alice Smith"
    assert result[1]["name"] == "Bob Jones"


def test_upper_mode():
    result = capwords_column(_rows(), "city", mode="upper")
    assert result[0]["city"] == "NEW YORK"
    assert result[1]["city"] == "LOS ANGELES"


def test_lower_mode():
    result = capwords_column(_rows(), "name", mode="lower")
    assert result[1]["name"] == "bob jones"


def test_sentence_mode():
    result = capwords_column(_rows(), "name", mode="sentence")
    assert result[0]["name"] == "Alice smith"
    assert result[1]["name"] == "Bob jones"


def test_sentence_empty_value_passthrough():
    result = capwords_column(_rows(), "name", mode="sentence")
    assert result[3]["name"] == ""


def test_dest_column_written():
    result = capwords_column(_rows(), "name", mode="title", dest="name_clean")
    assert "name_clean" in result[0]
    assert result[0]["name_clean"] == "Alice Smith"
    # original column unchanged
    assert result[0]["name"] == "alice smith"


def test_does_not_mutate_original():
    original = _rows()
    capwords_column(original, "name", mode="upper")
    assert original[0]["name"] == "alice smith"


def test_unknown_mode_raises():
    with pytest.raises(ValueError, match="Unknown mode"):
        capwords_column(_rows(), "name", mode="camel")


def test_missing_column_becomes_empty():
    rows = [{"other": "hello"}]
    result = capwords_column(rows, "name", mode="title")
    assert result[0]["name"] == ""


def test_capwords_many_applies_all_specs():
    specs = [
        {"column": "name", "mode": "title"},
        {"column": "city", "mode": "upper"},
    ]
    result = capwords_many(_rows(), specs)
    assert result[0]["name"] == "Alice Smith"
    assert result[0]["city"] == "NEW YORK"


def test_capwords_many_with_dest():
    specs = [{"column": "name", "mode": "lower", "dest": "name_lower"}]
    result = capwords_many(_rows(), specs)
    assert result[0]["name_lower"] == "alice smith"
    assert result[0]["name"] == "alice smith"


def test_cap_sentence_helper():
    assert _cap_sentence("hello WORLD") == "Hello world"
    assert _cap_sentence("") == ""
    assert _cap_sentence("x") == "X"
