import pytest
from csvwrangler.pivot_long import wide_to_long, long_to_wide


def _wide_rows():
    return [
        {"id": "1", "name": "Alice", "jan": "100", "feb": "200", "mar": "150"},
        {"id": "2", "name": "Bob",   "jan": "80",  "feb": "90",  "mar": "110"},
    ]


def _long_rows():
    return [
        {"id": "1", "month": "jan", "sales": "100"},
        {"id": "1", "month": "feb", "sales": "200"},
        {"id": "2", "month": "jan", "sales": "80"},
        {"id": "2", "month": "feb", "sales": "90"},
    ]


def test_wide_to_long_row_count():
    result = wide_to_long(_wide_rows(), id_cols=["id", "name"], value_cols=["jan", "feb", "mar"])
    assert len(result) == 6  # 2 rows * 3 value cols


def test_wide_to_long_field_names():
    result = wide_to_long(_wide_rows(), id_cols=["id", "name"], value_cols=["jan"])
    assert set(result[0].keys()) == {"id", "name", "variable", "value"}


def test_wide_to_long_custom_var_val_names():
    result = wide_to_long(
        _wide_rows(), id_cols=["id"], value_cols=["jan"],
        var_name="month", val_name="sales"
    )
    assert "month" in result[0]
    assert "sales" in result[0]


def test_wide_to_long_values_correct():
    result = wide_to_long(_wide_rows(), id_cols=["id", "name"], value_cols=["jan", "feb"])
    alice_jan = next(r for r in result if r["id"] == "1" and r["variable"] == "jan")
    assert alice_jan["value"] == "100"


def test_wide_to_long_infers_value_cols():
    # When value_cols is None, all non-id cols become value cols
    result = wide_to_long(_wide_rows(), id_cols=["id", "name"])
    assert len(result) == 6


def test_wide_to_long_id_cols_repeated():
    result = wide_to_long(_wide_rows(), id_cols=["id", "name"], value_cols=["jan", "feb"])
    alice_rows = [r for r in result if r["id"] == "1"]
    assert len(alice_rows) == 2
    assert all(r["name"] == "Alice" for r in alice_rows)


def test_wide_to_long_empty_rows():
    assert wide_to_long([], id_cols=["id"]) == []


def test_long_to_wide_row_count():
    result = long_to_wide(_long_rows(), id_cols=["id"], var_col="month", val_col="sales")
    assert len(result) == 2


def test_long_to_wide_column_names():
    result = long_to_wide(_long_rows(), id_cols=["id"], var_col="month", val_col="sales")
    assert "jan" in result[0]
    assert "feb" in result[0]


def test_long_to_wide_values_correct():
    result = long_to_wide(_long_rows(), id_cols=["id"], var_col="month", val_col="sales")
    row1 = next(r for r in result if r["id"] == "1")
    assert row1["jan"] == "100"
    assert row1["feb"] == "200"


def test_long_to_wide_fill_missing():
    rows = [
        {"id": "1", "month": "jan", "sales": "100"},
        {"id": "2", "month": "feb", "sales": "90"},
    ]
    result = long_to_wide(rows, id_cols=["id"], var_col="month", val_col="sales", fill="0")
    row1 = next(r for r in result if r["id"] == "1")
    assert row1.get("feb") == "0"


def test_long_to_wide_empty_rows():
    assert long_to_wide([], id_cols=["id"], var_col="month", val_col="sales") == []
