import pytest
from csvwrangler.conditional import conditional_set, conditional_many, _eval_condition


def _rows():
    return [
        {"name": "Alice", "score": "85", "grade": ""},
        {"name": "Bob", "score": "55", "grade": ""},
        {"name": "Carol", "score": "95", "grade": ""},
        {"name": "", "score": "70", "grade": ""},
    ]


def test_gt_sets_then_val():
    result = conditional_set(_rows(), dest="grade", column="score", op="gt",
                             value="80", then_val="pass", else_val="fail")
    assert result[0]["grade"] == "pass"  # 85 > 80
    assert result[1]["grade"] == "fail"  # 55 > 80 false
    assert result[2]["grade"] == "pass"  # 95 > 80


def test_lte_numeric():
    result = conditional_set(_rows(), dest="flag", column="score", op="lte",
                             value="60", then_val="low", else_val="ok")
    assert result[0]["flag"] == "ok"
    assert result[1]["flag"] == "low"  # 55 <= 60


def test_eq_string():
    result = conditional_set(_rows(), dest="label", column="name", op="eq",
                             value="Alice", then_val="found", else_val="other")
    assert result[0]["label"] == "found"
    assert result[1]["label"] == "other"


def test_contains():
    result = conditional_set(_rows(), dest="has_a", column="name", op="contains",
                             value="li", then_val="yes", else_val="no")
    assert result[0]["has_a"] == "yes"  # Alice contains 'li'
    assert result[1]["has_a"] == "no"


def test_startswith():
    result = conditional_set(_rows(), dest="a_name", column="name", op="startswith",
                             value="A", then_val="1", else_val="0")
    assert result[0]["a_name"] == "1"
    assert result[1]["a_name"] == "0"


def test_empty_op():
    result = conditional_set(_rows(), dest="missing", column="name", op="empty",
                             value="", then_val="yes", else_val="no")
    assert result[3]["missing"] == "yes"  # empty name
    assert result[0]["missing"] == "no"


def test_notempty_op():
    result = conditional_set(_rows(), dest="present", column="name", op="notempty",
                             value="", then_val="yes", else_val="no")
    assert result[0]["present"] == "yes"
    assert result[3]["present"] == "no"


def test_else_val_none_preserves_existing():
    rows = [{"col": "5", "dest": "existing"}]
    result = conditional_set(rows, dest="dest", column="col", op="gt",
                             value="10", then_val="big")
    assert result[0]["dest"] == "existing"  # else_val=None keeps original


def test_does_not_mutate_original():
    rows = _rows()
    original = [dict(r) for r in rows]
    conditional_set(rows, dest="grade", column="score", op="gt",
                    value="80", then_val="pass", else_val="fail")
    for orig, row in zip(original, rows):
        assert orig == row


def test_conditional_many_applies_in_order():
    rows = [{"score": "90", "tier": "", "flag": ""}]
    specs = [
        {"dest": "tier", "column": "score", "op": "gte", "value": "80",
         "then_val": "high", "else_val": "low"},
        {"dest": "flag", "column": "tier", "op": "eq", "value": "high",
         "then_val": "1", "else_val": "0"},
    ]
    result = conditional_many(rows, specs)
    assert result[0]["tier"] == "high"
    assert result[0]["flag"] == "1"


def test_ne_numeric():
    rows = [{"val": "5"}, {"val": "10"}]
    result = conditional_set(rows, dest="out", column="val", op="ne",
                             value="5", then_val="diff", else_val="same")
    assert result[0]["out"] == "same"
    assert result[1]["out"] == "diff"


def test_unknown_op_returns_false():
    assert _eval_condition({"x": "hello"}, "x", "unknown_op", "hello") is False
