import pytest
from csvwrangler.convert import convert_column, convert_all

ROWS = [
    {"name": "  Alice ", "age": "30", "score": "9.75"},
    {"name": "  BOB ", "age": "25", "score": "8.1"},
    {"name": "Charlie", "age": "not_a_num", "score": "7"},
]


def test_to_int_valid():
    result = convert_column(ROWS, "age", "int")
    assert result[0]["age"] == "30"
    assert result[1]["age"] == "25"


def test_to_int_invalid_passthrough():
    result = convert_column(ROWS, "age", "int")
    assert result[2]["age"] == "not_a_num"


def test_to_float_basic():
    result = convert_column(ROWS, "score", "float")
    assert result[0]["score"] == "9.75"
    assert result[2]["score"] == "7.0"


def test_to_float_with_decimals():
    result = convert_column(ROWS, "score", "float", decimals=1)
    assert result[0]["score"] == "9.8"
    assert result[2]["score"] == "7.0"


def test_to_upper():
    result = convert_column(ROWS, "name", "upper")
    assert result[0]["name"] == "  ALICE "
    assert result[1]["name"] == "  BOB "


def test_to_lower():
    result = convert_column(ROWS, "name", "lower")
    assert result[0]["name"] == "  alice "
    assert result[1]["name"] == "  bob "


def test_to_strip():
    result = convert_column(ROWS, "name", "strip")
    assert result[0]["name"] == "Alice"
    assert result[1]["name"] == "BOB"


def test_unknown_conversion_raises():
    with pytest.raises(ValueError, match="Unknown conversion"):
        convert_column(ROWS, "name", "titlecase")


def test_missing_column_leaves_row_unchanged():
    result = convert_column(ROWS, "nonexistent", "upper")
    assert result[0] == ROWS[0]


def test_convert_all():
    result = convert_all(ROWS, {"name": "strip", "age": "int"})
    assert result[0]["name"] == "Alice"
    assert result[1]["age"] == "25"


def test_original_rows_not_mutated():
    original_name = ROWS[0]["name"]
    convert_column(ROWS, "name", "strip")
    assert ROWS[0]["name"] == original_name
