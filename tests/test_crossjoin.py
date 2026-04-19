import pytest
from csvwrangler.crossjoin import cross_join, conditional_join, anti_join, semi_join

LEFT = [
    {"id": "1", "name": "Alice"},
    {"id": "2", "name": "Bob"},
]

RIGHT = [
    {"id": "1", "score": "90"},
    {"id": "3", "score": "75"},
]


def test_cross_join_row_count():
    result = cross_join(LEFT, RIGHT)
    assert len(result) == 4


def test_cross_join_merges_fields():
    result = cross_join(LEFT, RIGHT)
    assert "name" in result[0]
    assert "score" in result[0]


def test_cross_join_conflict_prefixed():
    result = cross_join(LEFT, RIGHT)
    # 'id' exists in both, right side should be prefixed
    assert "right_id" in result[0]
    assert result[0]["id"] == "1"
    assert result[0]["right_id"] == "1"


def test_cross_join_empty_left():
    assert cross_join([], RIGHT) == []


def test_cross_join_empty_right():
    assert cross_join(LEFT, []) == []


def test_conditional_join_basic():
    result = conditional_join(
        LEFT, RIGHT, lambda l, r: l["id"] == r["id"]
    )
    assert len(result) == 1
    assert result[0]["name"] == "Alice"
    assert result[0]["score"] == "90"


def test_conditional_join_no_matches():
    result = conditional_join(
        LEFT, RIGHT, lambda l, r: False
    )
    assert result == []


def test_conditional_join_custom_prefix():
    result = conditional_join(
        LEFT, RIGHT, lambda l, r: l["id"] == r["id"], prefix="r_"
    )
    assert "r_id" in result[0]


def test_anti_join_basic():
    result = anti_join(LEFT, RIGHT, keys=["id"])
    assert len(result) == 1
    assert result[0]["name"] == "Bob"


def test_anti_join_no_matches_in_right():
    result = anti_join(LEFT, [], keys=["id"])
    assert result == LEFT


def test_anti_join_all_matched():
    right = [{"id": "1"}, {"id": "2"}]
    result = anti_join(LEFT, right, keys=["id"])
    assert result == []


def test_semi_join_basic():
    result = semi_join(LEFT, RIGHT, keys=["id"])
    assert len(result) == 1
    assert result[0]["name"] == "Alice"


def test_semi_join_empty_right():
    assert semi_join(LEFT, [], keys=["id"]) == []


def test_semi_join_all_match():
    right = [{"id": "1"}, {"id": "2"}]
    result = semi_join(LEFT, right, keys=["id"])
    assert len(result) == 2
