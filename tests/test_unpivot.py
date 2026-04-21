import pytest
from csvwrangler.unpivot import unpivot_rows, unpivot_summary


def _rows():
    return [
        {"name": "Alice", "math": "90", "english": "85", "science": "92"},
        {"name": "Bob", "math": "78", "english": "88", "science": "80"},
    ]


def test_basic_unpivot_row_count():
    result = unpivot_rows(_rows(), id_cols=["name"])
    # 2 rows * 3 value cols = 6
    assert len(result) == 6


def test_basic_unpivot_fields_present():
    result = unpivot_rows(_rows(), id_cols=["name"])
    assert "name" in result[0]
    assert "variable" in result[0]
    assert "value" in result[0]


def test_unpivot_variable_values():
    result = unpivot_rows(_rows(), id_cols=["name"])
    variables = {r["variable"] for r in result}
    assert variables == {"math", "english", "science"}


def test_unpivot_value_correct():
    result = unpivot_rows(_rows(), id_cols=["name"])
    alice_math = next(r for r in result if r["name"] == "Alice" and r["variable"] == "math")
    assert alice_math["value"] == "90"


def test_unpivot_custom_var_val_names():
    result = unpivot_rows(_rows(), id_cols=["name"], var_name="subject", val_name="score")
    assert "subject" in result[0]
    assert "score" in result[0]


def test_unpivot_explicit_value_cols():
    result = unpivot_rows(_rows(), id_cols=["name"], value_cols=["math", "english"])
    assert len(result) == 4
    variables = {r["variable"] for r in result}
    assert variables == {"math", "english"}
    assert "science" not in variables


def test_unpivot_empty_rows():
    result = unpivot_rows([], id_cols=["name"])
    assert result == []


def test_unpivot_does_not_mutate_original():
    rows = _rows()
    original = [dict(r) for r in rows]
    unpivot_rows(rows, id_cols=["name"])
    assert rows == original


def test_unpivot_multiple_id_cols():
    rows = [
        {"region": "north", "year": "2023", "q1": "100", "q2": "200"},
        {"region": "south", "year": "2023", "q1": "150", "q2": "250"},
    ]
    result = unpivot_rows(rows, id_cols=["region", "year"])
    assert len(result) == 4
    assert "region" in result[0]
    assert "year" in result[0]


def test_summary_basic():
    s = unpivot_summary(_rows(), id_cols=["name"])
    assert s["input_rows"] == 2
    assert s["output_rows"] == 6
    assert set(s["value_cols"]) == {"math", "english", "science"}


def test_summary_empty():
    s = unpivot_summary([], id_cols=["name"])
    assert s["output_rows"] == 0
    assert s["value_cols"] == []
