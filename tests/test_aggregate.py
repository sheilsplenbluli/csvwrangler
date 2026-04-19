import pytest
from csvwrangler.aggregate import aggregate_rows

ROWS = [
    {"dept": "eng", "name": "alice", "salary": "90000"},
    {"dept": "eng", "name": "bob", "salary": "80000"},
    {"dept": "hr", "name": "carol", "salary": "70000"},
    {"dept": "hr", "name": "dave", "salary": "60000"},
    {"dept": "eng", "name": "eve", "salary": "100000"},
]


def test_sum():
    result = aggregate_rows(ROWS, ["dept"], {"total": "sum:salary"})
    by_dept = {r["dept"]: r for r in result}
    assert by_dept["eng"]["total"] == "270000.0"
    assert by_dept["hr"]["total"] == "130000.0"


def test_count():
    result = aggregate_rows(ROWS, ["dept"], {"n": "count:name"})
    by_dept = {r["dept"]: r for r in result}
    assert by_dept["eng"]["n"] == "3"
    assert by_dept["hr"]["n"] == "2"


def test_mean():
    result = aggregate_rows(ROWS, ["dept"], {"avg": "mean:salary"})
    by_dept = {r["dept"]: r for r in result}
    assert float(by_dept["eng"]["avg"]) == pytest.approx(90000.0)
    assert float(by_dept["hr"]["avg"]) == pytest.approx(65000.0)


def test_min_max():
    result = aggregate_rows(ROWS, ["dept"], {"lo": "min:salary", "hi": "max:salary"})
    by_dept = {r["dept"]: r for r in result}
    assert by_dept["eng"]["lo"] == "80000.0"
    assert by_dept["eng"]["hi"] == "100000.0"


def test_first_last():
    result = aggregate_rows(ROWS, ["dept"], {"first_name": "first:name", "last_name": "last:name"})
    by_dept = {r["dept"]: r for r in result}
    assert by_dept["eng"]["first_name"] == "alice"
    assert by_dept["eng"]["last_name"] == "eve"


def test_unknown_func_raises():
    with pytest.raises(ValueError, match="Unknown aggregation"):
        aggregate_rows(ROWS, ["dept"], {"x": "median:salary"})


def test_non_numeric_returns_empty():
    result = aggregate_rows(ROWS, ["dept"], {"s": "sum:name"})
    for r in result:
        assert r["s"] == ""


def test_empty_rows():
    result = aggregate_rows([], ["dept"], {"n": "count:salary"})
    assert result == []


def test_multiple_group_keys():
    """Group by more than one column and verify aggregation still works."""
    rows = [
        {"dept": "eng", "level": "senior", "salary": "120000"},
        {"dept": "eng", "level": "senior", "salary": "110000"},
        {"dept": "eng", "level": "junior", "salary": "80000"},
        {"dept": "hr", "level": "senior", "salary": "90000"},
    ]
    result = aggregate_rows(rows, ["dept", "level"], {"n": "count:salary", "total": "sum:salary"})
    by_key = {(r["dept"], r["level"]): r for r in result}
    assert by_key[("eng", "senior")]["n"] == "2"
    assert by_key[("eng", "senior")]["total"] == "230000.0"
    assert by_key[("eng", "junior")]["n"] == "1"
    assert by_key[("hr", "senior")]["total"] == "90000.0"
