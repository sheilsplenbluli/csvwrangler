import pytest
from csvwrangler.levenshtein import (
    _levenshtein,
    distance_column,
    nearest_match,
    similarity_score,
)


def _rows():
    return [
        {"a": "kitten", "b": "sitting"},
        {"a": "hello", "b": "hello"},
        {"a": "abc", "b": ""},
        {"a": "", "b": "xyz"},
    ]


def test_levenshtein_classic():
    assert _levenshtein("kitten", "sitting") == 3


def test_levenshtein_identical():
    assert _levenshtein("hello", "hello") == 0


def test_levenshtein_empty_a():
    assert _levenshtein("", "abc") == 3


def test_levenshtein_empty_b():
    assert _levenshtein("abc", "") == 3


def test_levenshtein_both_empty():
    assert _levenshtein("", "") == 0


def test_distance_column_adds_column():
    rows = _rows()
    result = distance_column(rows, "a", "b")
    assert "a_dist_b" in result[0]


def test_distance_column_values():
    rows = _rows()
    result = distance_column(rows, "a", "b")
    assert result[0]["a_dist_b"] == "3"
    assert result[1]["a_dist_b"] == "0"
    assert result[2]["a_dist_b"] == "3"
    assert result[3]["a_dist_b"] == "3"


def test_distance_column_custom_dest():
    rows = [{"x": "cat", "y": "car"}]
    result = distance_column(rows, "x", "y", dest="edit_dist")
    assert "edit_dist" in result[0]
    assert result[0]["edit_dist"] == "1"


def test_distance_column_ignore_case():
    rows = [{"a": "Hello", "b": "hello"}]
    result = distance_column(rows, "a", "b", ignore_case=True)
    assert result[0]["a_dist_b"] == "0"


def test_distance_column_does_not_mutate():
    rows = [{"a": "foo", "b": "bar"}]
    original = dict(rows[0])
    distance_column(rows, "a", "b")
    assert rows[0] == original


def test_nearest_match_basic():
    rows = [{"name": "colour"}]
    result = nearest_match(rows, "name", ["color", "colon", "collar"])
    assert result[0]["name_nearest"] == "color"


def test_nearest_match_exact():
    rows = [{"name": "apple"}]
    result = nearest_match(rows, "name", ["apple", "apply", "maple"])
    assert result[0]["name_nearest"] == "apple"


def test_nearest_match_ignore_case():
    rows = [{"name": "APPLE"}]
    result = nearest_match(rows, "name", ["apple", "apply"], ignore_case=True)
    assert result[0]["name_nearest"] == "apple"


def test_nearest_match_custom_dest():
    rows = [{"word": "teh"}]
    result = nearest_match(rows, "word", ["the", "ten"], dest="corrected")
    assert "corrected" in result[0]


def test_similarity_score_identical():
    rows = [{"a": "hello", "b": "hello"}]
    result = similarity_score(rows, "a", "b")
    assert result[0]["a_sim_b"] == "1.0"


def test_similarity_score_range():
    rows = [{"a": "kitten", "b": "sitting"}]
    result = similarity_score(rows, "a", "b")
    score = float(result[0]["a_sim_b"])
    assert 0.0 <= score <= 1.0


def test_similarity_score_custom_dest():
    rows = [{"x": "cat", "y": "car"}]
    result = similarity_score(rows, "x", "y", dest="sim")
    assert "sim" in result[0]
