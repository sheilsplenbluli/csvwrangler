"""Tests for csvwrangler.phonetic."""
import pytest
from csvwrangler.phonetic import (
    _soundex,
    _metaphone,
    soundex_column,
    metaphone_column,
    phonetic_many,
)


def _rows(*names):
    return [{"name": n} for n in names]


# ---------------------------------------------------------------------------
# _soundex unit tests
# ---------------------------------------------------------------------------

def test_soundex_robert():
    assert _soundex("Robert") == "R163"


def test_soundex_rupert():
    # Rupert and Robert share the same Soundex
    assert _soundex("Rupert") == _soundex("Robert")


def test_soundex_empty_string():
    assert _soundex("") == ""


def test_soundex_single_char():
    code = _soundex("A")
    assert code == "A000"


def test_soundex_all_vowels_after_first():
    code = _soundex("Aeiou")
    assert code.startswith("A")
    assert len(code) == 4


def test_soundex_smith_vs_smythe():
    assert _soundex("Smith") == _soundex("Smythe")


# ---------------------------------------------------------------------------
# _metaphone unit tests
# ---------------------------------------------------------------------------

def test_metaphone_empty_string():
    assert _metaphone("") == ""


def test_metaphone_keeps_leading_vowel():
    code = _metaphone("Apple")
    assert code.startswith("A")


def test_metaphone_drops_silent_h():
    code = _metaphone("What")
    assert "H" not in code


def test_metaphone_max_six_chars():
    code = _metaphone("Supercalifragilistic")
    assert len(code) <= 6


# ---------------------------------------------------------------------------
# soundex_column
# ---------------------------------------------------------------------------

def test_soundex_column_adds_field():
    rows = _rows("Alice", "Bob")
    result = soundex_column(rows, "name")
    assert "name_soundex" in result[0]
    assert "name_soundex" in result[1]


def test_soundex_column_custom_dest():
    rows = _rows("Alice")
    result = soundex_column(rows, "name", dest="sx")
    assert "sx" in result[0]


def test_soundex_column_does_not_mutate():
    rows = _rows("Alice")
    original_keys = set(rows[0].keys())
    soundex_column(rows, "name")
    assert set(rows[0].keys()) == original_keys


def test_soundex_column_missing_col_is_empty():
    rows = [{"other": "x"}]
    result = soundex_column(rows, "name")
    assert result[0]["name_soundex"] == ""


# ---------------------------------------------------------------------------
# metaphone_column
# ---------------------------------------------------------------------------

def test_metaphone_column_adds_field():
    rows = _rows("Smith", "Smythe")
    result = metaphone_column(rows, "name")
    assert "name_metaphone" in result[0]


def test_metaphone_column_same_code_for_similar_names():
    rows = _rows("Smith", "Smythe")
    result = metaphone_column(rows, "name")
    assert result[0]["name_metaphone"] == result[1]["name_metaphone"]


def test_metaphone_column_does_not_mutate():
    rows = _rows("Bob")
    original_keys = set(rows[0].keys())
    metaphone_column(rows, "name")
    assert set(rows[0].keys()) == original_keys


# ---------------------------------------------------------------------------
# phonetic_many
# ---------------------------------------------------------------------------

def test_phonetic_many_applies_both_methods():
    rows = _rows("Alice", "Bob")
    specs = [
        {"col": "name", "method": "soundex"},
        {"col": "name", "method": "metaphone"},
    ]
    result = phonetic_many(rows, specs)
    assert "name_soundex" in result[0]
    assert "name_metaphone" in result[0]


def test_phonetic_many_defaults_to_soundex():
    rows = _rows("Carol")
    result = phonetic_many(rows, [{"col": "name"}])
    assert "name_soundex" in result[0]


def test_phonetic_many_custom_dest():
    rows = _rows("Dana")
    result = phonetic_many(rows, [{"col": "name", "method": "soundex", "dest": "code"}])
    assert "code" in result[0]
