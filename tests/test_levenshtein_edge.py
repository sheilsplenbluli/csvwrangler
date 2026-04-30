from csvwrangler.levenshtein import (
    _levenshtein,
    distance_column,
    nearest_match,
    similarity_score,
)


def test_single_char_substitution():
    assert _levenshtein("a", "b") == 1


def test_single_char_insertion():
    assert _levenshtein("a", "ab") == 1


def test_single_char_deletion():
    assert _levenshtein("ab", "a") == 1


def test_unicode_strings():
    # café vs cafe: one substitution
    assert _levenshtein("café", "cafe") == 1


def test_distance_column_missing_col_uses_empty():
    rows = [{"a": "hello"}]  # col b missing
    result = distance_column(rows, "a", "b")
    # distance from "hello" to "" is 5
    assert result[0]["a_dist_b"] == "5"


def test_distance_column_preserves_existing_fields():
    rows = [{"a": "cat", "b": "car", "extra": "keep"}]
    result = distance_column(rows, "a", "b")
    assert result[0]["extra"] == "keep"


def test_nearest_match_empty_candidates_returns_empty():
    rows = [{"name": "hello"}]
    result = nearest_match(rows, "name", [])
    assert result[0]["name_nearest"] == ""


def test_nearest_match_single_candidate():
    rows = [{"name": "speling"}]
    result = nearest_match(rows, "name", ["spelling"])
    assert result[0]["name_nearest"] == "spelling"


def test_nearest_match_does_not_mutate():
    rows = [{"name": "hello"}]
    original = dict(rows[0])
    nearest_match(rows, "name", ["hello", "world"])
    assert rows[0] == original


def test_similarity_both_empty():
    rows = [{"a": "", "b": ""}]
    result = similarity_score(rows, "a", "b")
    # max_len is clamped to 1, dist=0, so score=1.0
    assert result[0]["a_sim_b"] == "1.0"


def test_similarity_completely_different():
    rows = [{"a": "abc", "b": "xyz"}]
    result = similarity_score(rows, "a", "b")
    score = float(result[0]["a_sim_b"])
    assert score == 0.0


def test_similarity_does_not_mutate():
    rows = [{"a": "foo", "b": "bar"}]
    original = dict(rows[0])
    similarity_score(rows, "a", "b")
    assert rows[0] == original


def test_empty_rows_returns_empty():
    assert distance_column([], "a", "b") == []
    assert nearest_match([], "a", ["x"]) == []
    assert similarity_score([], "a", "b") == []
