"""Edge-case tests for csvwrangler.phonetic."""
from csvwrangler.phonetic import _soundex, _metaphone, soundex_column, phonetic_many


def test_soundex_pads_to_four_chars():
    code = _soundex("Lee")
    assert len(code) == 4
    assert code == "L000"


def test_soundex_truncates_to_four_chars():
    code = _soundex("Tschaikowsky")
    assert len(code) == 4


def test_soundex_case_insensitive():
    assert _soundex("robert") == _soundex("ROBERT")


def test_soundex_whitespace_stripped():
    assert _soundex("  Ann  ") == _soundex("Ann")


def test_soundex_numeric_input_returns_code():
    # Digits don't appear in the table so they map to '0'; first char kept
    code = _soundex("123")
    assert code.startswith("1")


def test_metaphone_drops_silent_w():
    code = _metaphone("Write")
    assert "W" not in code


def test_metaphone_collapses_repeated_consonants():
    code1 = _metaphone("Butter")
    code2 = _metaphone("Buter")
    assert code1 == code2


def test_metaphone_case_insensitive():
    assert _metaphone("Smith") == _metaphone("smith")


def test_soundex_column_preserves_other_fields():
    rows = [{"name": "Alice", "age": "30"}]
    result = soundex_column(rows, "name")
    assert result[0]["age"] == "30"


def test_phonetic_many_empty_specs_returns_unchanged():
    rows = [{"name": "Alice"}]
    result = phonetic_many(rows, [])
    assert result == rows


def test_phonetic_many_empty_rows():
    result = phonetic_many([], [{"col": "name"}])
    assert result == []
