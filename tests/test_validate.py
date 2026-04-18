import pytest
from csvwrangler.validate import validate_column, validate_all


ROWS = [
    {"name": "Alice", "age": "30", "status": "active"},
    {"name": "Bob", "age": "not_a_number", "status": "inactive"},
    {"name": "", "age": "25", "status": "pending"},
    {"name": "Dana", "age": "", "status": "active"},
    {"name": "Eve", "age": "28", "status": "unknown"},
]


def test_numeric_valid_passes():
    viols = validate_column(ROWS, "age", dtype="numeric")
    assert len(viols) == 1
    assert viols[0]["row"] == 1
    assert viols[0]["reason"] == "not numeric"


def test_empty_not_allowed():
    viols = validate_column(ROWS, "name", allow_empty=False)
    assert any(v["row"] == 2 for v in viols)


def test_empty_allowed_by_default():
    viols = validate_column(ROWS, "name")
    assert viols == []


def test_allowed_values():
    viols = validate_column(ROWS, "status", allowed=["active", "inactive"])
    assert len(viols) == 2
    reasons = {v["value"] for v in viols}
    assert "pending" in reasons
    assert "unknown" in reasons


def test_empty_skipped_for_allowed_check():
    # row with empty age should not trigger allowed check
    viols = validate_column(ROWS, "age", allowed=["30", "25", "28"])
    # "not_a_number" violates, empty is skipped
    assert any(v["value"] == "not_a_number" for v in viols)
    assert not any(v["value"] == "" for v in viols)


def test_validate_all_aggregates():
    rules = [
        {"column": "age", "dtype": "numeric"},
        {"column": "status", "allowed": ["active", "inactive"]},
    ]
    results = validate_all(ROWS, rules)
    assert "age" in results
    assert "status" in results


def test_validate_all_no_violations():
    rows = [{"x": "1"}, {"x": "2"}]
    results = validate_all(rows, [{"column": "x", "dtype": "numeric"}])
    assert results == {}


def test_combined_dtype_and_empty():
    viols = validate_column(ROWS, "age", dtype="numeric", allow_empty=False)
    reasons = [v["reason"] for v in viols]
    assert "not numeric" in reasons
    assert "empty value" in reasons
