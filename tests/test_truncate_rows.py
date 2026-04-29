import pytest
from csvwrangler.truncate_rows import (
    limit_rows,
    offset_rows,
    limit_offset,
    keep_while,
    drop_while,
    truncate_rows_summary,
)


def _rows(n: int):
    return [{"id": str(i), "val": "x"} for i in range(n)]


# --- limit_rows ---

def test_limit_returns_first_n():
    rows = _rows(10)
    result = limit_rows(rows, 3)
    assert len(result) == 3
    assert result[0]["id"] == "0"
    assert result[2]["id"] == "2"


def test_limit_larger_than_rows_returns_all():
    rows = _rows(5)
    assert len(limit_rows(rows, 100)) == 5


def test_limit_zero_returns_empty():
    assert limit_rows(_rows(5), 0) == []


def test_limit_negative_raises():
    with pytest.raises(ValueError):
        limit_rows(_rows(5), -1)


def test_limit_does_not_mutate_original():
    rows = _rows(5)
    limit_rows(rows, 2)
    assert len(rows) == 5


# --- offset_rows ---

def test_offset_skips_first_n():
    rows = _rows(5)
    result = offset_rows(rows, 2)
    assert len(result) == 3
    assert result[0]["id"] == "2"


def test_offset_zero_returns_all():
    rows = _rows(5)
    assert len(offset_rows(rows, 0)) == 5


def test_offset_beyond_length_returns_empty():
    assert offset_rows(_rows(3), 10) == []


def test_offset_negative_raises():
    with pytest.raises(ValueError):
        offset_rows(_rows(5), -1)


# --- limit_offset ---

def test_limit_offset_pagination():
    rows = _rows(10)
    result = limit_offset(rows, limit=3, offset=4)
    assert len(result) == 3
    assert result[0]["id"] == "4"


def test_limit_offset_default_offset_zero():
    rows = _rows(5)
    assert limit_offset(rows, limit=2) == limit_rows(rows, 2)


# --- keep_while ---

def test_keep_while_stops_at_first_mismatch():
    rows = [
        {"grp": "a", "v": "1"},
        {"grp": "a", "v": "2"},
        {"grp": "b", "v": "3"},
        {"grp": "a", "v": "4"},
    ]
    result = keep_while(rows, "grp", "a")
    assert len(result) == 2


def test_keep_while_all_match():
    rows = [{"grp": "a"} for _ in range(4)]
    assert len(keep_while(rows, "grp", "a")) == 4


def test_keep_while_none_match_returns_empty():
    rows = [{"grp": "b"}]
    assert keep_while(rows, "grp", "a") == []


# --- drop_while ---

def test_drop_while_skips_leading_matches():
    rows = [
        {"grp": "a"},
        {"grp": "a"},
        {"grp": "b"},
        {"grp": "a"},
    ]
    result = drop_while(rows, "grp", "a")
    assert len(result) == 2
    assert result[0]["grp"] == "b"


def test_drop_while_no_leading_match_returns_all():
    rows = [{"grp": "b"}, {"grp": "a"}]
    assert len(drop_while(rows, "grp", "a")) == 2


# --- truncate_rows_summary ---

def test_summary_basic():
    rows = _rows(10)
    s = truncate_rows_summary(rows, limit=3, offset=2)
    assert s["total"] == 10
    assert s["kept"] == 3
    assert s["dropped"] == 7


def test_summary_no_limit():
    rows = _rows(5)
    s = truncate_rows_summary(rows, limit=None, offset=1)
    assert s["kept"] == 4
