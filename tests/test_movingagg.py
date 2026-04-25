import pytest
from csvwrangler.movingagg import expanding_agg, expanding_many


def _rows():
    return [
        {"name": "a", "val": "10"},
        {"name": "b", "val": "20"},
        {"name": "c", "val": "30"},
        {"name": "d", "val": ""},
        {"name": "e", "val": "40"},
    ]


def test_expanding_sum_default_dest():
    result = expanding_agg(_rows(), "val", "sum")
    assert result[0]["val_exp_sum"] == "10.0"
    assert result[1]["val_exp_sum"] == "30.0"
    assert result[2]["val_exp_sum"] == "60.0"


def test_expanding_sum_skips_non_numeric():
    result = expanding_agg(_rows(), "val", "sum")
    # row index 3 has empty val; cumulative sum stays at 60
    assert result[3]["val_exp_sum"] == "60.0"
    assert result[4]["val_exp_sum"] == "100.0"


def test_expanding_mean():
    result = expanding_agg(_rows(), "val", "mean")
    assert result[0]["val_exp_mean"] == "10.0"
    assert result[1]["val_exp_mean"] == "15.0"
    assert result[2]["val_exp_mean"] == "20.0"


def test_expanding_min():
    result = expanding_agg(_rows(), "val", "min")
    assert result[0]["val_exp_min"] == "10.0"
    assert result[2]["val_exp_min"] == "10.0"
    assert result[4]["val_exp_min"] == "10.0"


def test_expanding_max():
    result = expanding_agg(_rows(), "val", "max")
    assert result[0]["val_exp_max"] == "10.0"
    assert result[2]["val_exp_max"] == "30.0"
    assert result[4]["val_exp_max"] == "40.0"


def test_expanding_count():
    result = expanding_agg(_rows(), "val", "count")
    # empty string is skipped, so count after row 3 is still 3
    assert result[3]["val_exp_count"] == "3"
    assert result[4]["val_exp_count"] == "4"


def test_custom_dest_column():
    result = expanding_agg(_rows(), "val", "sum", dest="running_total")
    assert "running_total" in result[0]
    assert result[2]["running_total"] == "60.0"


def test_does_not_mutate_original():
    rows = _rows()
    expanding_agg(rows, "val", "sum")
    assert "val_exp_sum" not in rows[0]


def test_empty_rows_returns_empty():
    result = expanding_agg([], "val", "sum")
    assert result == []


def test_all_non_numeric_gives_empty_dest():
    rows = [{"val": "abc"}, {"val": "xyz"}]
    result = expanding_agg(rows, "val", "sum")
    assert result[0]["val_exp_sum"] == ""
    assert result[1]["val_exp_sum"] == ""


def test_unknown_agg_raises():
    with pytest.raises(ValueError, match="Unknown aggregation"):
        expanding_agg(_rows(), "val", "median")


def test_expanding_many_multiple_specs():
    specs = [
        {"column": "val", "agg": "sum"},
        {"column": "val", "agg": "count", "dest": "n"},
    ]
    result = expanding_many(_rows(), specs)
    assert "val_exp_sum" in result[0]
    assert "n" in result[0]
    assert result[2]["n"] == "3"
