import pytest
from csvwrangler.join import join_rows

LEFT = [
    {"id": "1", "name": "Alice"},
    {"id": "2", "name": "Bob"},
    {"id": "3", "name": "Carol"},
]

RIGHT = [
    {"id": "1", "dept": "Eng"},
    {"id": "2", "dept": "HR"},
    {"id": "4", "dept": "Sales"},
]


def test_inner_join_basic():
    result = join_rows(LEFT, RIGHT, on="id", how="inner")
    assert len(result) == 2
    ids = {r["id"] for r in result}
    assert ids == {"1", "2"}
    assert result[0]["dept"] == "Eng"


def test_left_join_keeps_unmatched_left():
    result = join_rows(LEFT, RIGHT, on="id", how="left")
    assert len(result) == 3
    carol = next(r for r in result if r["id"] == "3")
    assert carol["dept"] == ""


def test_right_join_keeps_unmatched_right():
    result = join_rows(LEFT, RIGHT, on="id", how="right")
    assert len(result) == 3
    sales = next(r for r in result if r["id"] == "4")
    assert sales["name"] == ""
    assert sales["dept"] == "Sales"


def test_inner_join_empty_left():
    result = join_rows([], RIGHT, on="id", how="inner")
    assert result == []


def test_inner_join_empty_right():
    result = join_rows(LEFT, [], on="id", how="inner")
    assert result == []


def test_column_collision_renamed():
    left = [{"id": "1", "name": "Alice"}]
    right = [{"id": "1", "name": "AliceR", "score": "99"}]
    result = join_rows(left, right, on="id", how="inner")
    assert len(result) == 1
    assert "name_y" in result[0]
    assert result[0]["name"] == "Alice"
    assert result[0]["name_y"] == "AliceR"
    assert result[0]["score"] == "99"


def test_invalid_how_raises():
    with pytest.raises(ValueError, match="Unknown join type"):
        join_rows(LEFT, RIGHT, on="id", how="outer")


def test_multiple_matches():
    right_multi = [
        {"id": "1", "tag": "a"},
        {"id": "1", "tag": "b"},
    ]
    result = join_rows(LEFT, right_multi, on="id", how="inner")
    assert len(result) == 2
    tags = {r["tag"] for r in result}
    assert tags == {"a", "b"}
