import pytest
from csvwrangler.pivot_stack import stack_columns, unstack_column, stack_summary


def _rows():
    return [
        {"region": "North", "year": "2022", "sales": "100", "cost": "80"},
        {"region": "South", "year": "2022", "sales": "200", "cost": "150"},
        {"region": "North", "year": "2023", "sales": "120", "cost": "90"},
    ]


def test_stack_row_count():
    rows = _rows()
    result = stack_columns(rows, id_cols=["region", "year"], value_cols=["sales", "cost"])
    assert len(result) == 6  # 3 rows * 2 value cols


def test_stack_variable_values():
    rows = _rows()
    result = stack_columns(rows, id_cols=["region", "year"], value_cols=["sales", "cost"])
    vars_ = [r["variable"] for r in result]
    assert vars_ == ["sales", "cost", "sales", "cost", "sales", "cost"]


def test_stack_value_correct():
    rows = _rows()
    result = stack_columns(rows, id_cols=["region", "year"], value_cols=["sales", "cost"])
    first = result[0]
    assert first["region"] == "North"
    assert first["year"] == "2022"
    assert first["variable"] == "sales"
    assert first["value"] == "100"


def test_stack_custom_col_names():
    rows = _rows()
    result = stack_columns(rows, id_cols=["region"], value_cols=["sales"], var_col="metric", val_col="amount")
    assert "metric" in result[0]
    assert "amount" in result[0]


def test_stack_empty_rows():
    result = stack_columns([], id_cols=["region"], value_cols=["sales"])
    assert result == []


def test_stack_does_not_mutate_original():
    rows = _rows()
    original = [dict(r) for r in rows]
    stack_columns(rows, id_cols=["region", "year"], value_cols=["sales", "cost"])
    assert rows == original


def test_unstack_row_count():
    rows = _rows()
    stacked = stack_columns(rows, id_cols=["region", "year"], value_cols=["sales", "cost"])
    result = unstack_column(stacked, id_cols=["region", "year"], var_col="variable", val_col="value")
    assert len(result) == 3


def test_unstack_columns_present():
    rows = _rows()
    stacked = stack_columns(rows, id_cols=["region", "year"], value_cols=["sales", "cost"])
    result = unstack_column(stacked, id_cols=["region", "year"], var_col="variable", val_col="value")
    assert "sales" in result[0]
    assert "cost" in result[0]


def test_unstack_values_correct():
    rows = _rows()
    stacked = stack_columns(rows, id_cols=["region", "year"], value_cols=["sales", "cost"])
    result = unstack_column(stacked, id_cols=["region", "year"], var_col="variable", val_col="value")
    north_2022 = next(r for r in result if r["region"] == "North" and r["year"] == "2022")
    assert north_2022["sales"] == "100"
    assert north_2022["cost"] == "80"


def test_unstack_fill_value():
    rows = [
        {"id": "1", "variable": "a", "value": "10"},
        {"id": "2", "variable": "b", "value": "20"},
    ]
    result = unstack_column(rows, id_cols=["id"], var_col="variable", val_col="value", fill="N/A")
    r1 = next(r for r in result if r["id"] == "1")
    assert r1.get("b") == "N/A"


def test_unstack_empty_rows():
    result = unstack_column([], id_cols=["region"], var_col="variable", val_col="value")
    assert result == []


def test_stack_summary_keys():
    rows = _rows()
    s = stack_summary(rows, id_cols=["region"], value_cols=["sales", "cost"])
    assert s["input_rows"] == 3
    assert s["output_rows"] == 6
    assert s["value_cols"] == ["sales", "cost"]
