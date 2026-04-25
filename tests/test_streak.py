import pytest
from csvwrangler.streak import streak_column, streak_any


def _rows():
    return [
        {"status": "win"},
        {"status": "win"},
        {"status": "loss"},
        {"status": "win"},
        {"status": "win"},
        {"status": "win"},
    ]


def test_streak_increments_on_match():
    rows = _rows()
    result = streak_column(rows, "status", "win")
    counts = [r["status_streak"] for r in result]
    assert counts == ["1", "2", "0", "1", "2", "3"]


def test_streak_resets_on_mismatch():
    rows = _rows()
    result = streak_column(rows, "status", "loss")
    counts = [r["status_streak"] for r in result]
    assert counts == ["0", "0", "1", "0", "0", "0"]


def test_streak_custom_dest():
    rows = _rows()
    result = streak_column(rows, "status", "win", dest="run")
    assert "run" in result[0]
    assert "status_streak" not in result[0]


def test_streak_does_not_mutate_original():
    rows = _rows()
    streak_column(rows, "status", "win")
    assert "status_streak" not in rows[0]


def test_streak_empty_rows():
    result = streak_column([], "status", "win")
    assert result == []


def test_streak_missing_column_treated_as_no_match():
    rows = [{"other": "x"}, {"other": "y"}]
    result = streak_column(rows, "status", "win")
    assert all(r["status_streak"] == "0" for r in result)


def test_streak_case_insensitive():
    rows = [{"val": "WIN"}, {"val": "Win"}, {"val": "win"}, {"val": "lose"}]
    result = streak_column(rows, "val", "win", case_sensitive=False)
    counts = [r["val_streak"] for r in result]
    assert counts == ["1", "2", "3", "0"]


def test_streak_case_sensitive_no_match():
    rows = [{"val": "WIN"}, {"val": "win"}]
    result = streak_column(rows, "val", "win", case_sensitive=True)
    counts = [r["val_streak"] for r in result]
    assert counts == ["0", "1"]


def test_streak_any_multiple_specs():
    rows = [
        {"a": "x", "b": "y"},
        {"a": "x", "b": "y"},
        {"a": "z", "b": "y"},
    ]
    result = streak_any(rows, [
        {"column": "a", "target": "x"},
        {"column": "b", "target": "y"},
    ])
    a_streaks = [r["a_streak"] for r in result]
    b_streaks = [r["b_streak"] for r in result]
    assert a_streaks == ["1", "2", "0"]
    assert b_streaks == ["1", "2", "3"]


def test_streak_all_match():
    rows = [{"v": "ok"} for _ in range(5)]
    result = streak_column(rows, "v", "ok")
    counts = [r["v_streak"] for r in result]
    assert counts == ["1", "2", "3", "4", "5"]


def test_streak_none_match():
    rows = [{"v": "no"} for _ in range(4)]
    result = streak_column(rows, "v", "yes")
    assert all(r["v_streak"] == "0" for r in result)
