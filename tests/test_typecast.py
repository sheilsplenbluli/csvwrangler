import pytest
from csvwrangler.typecast import typecast_column, typecast_many

ROWS = [
    {"name": "Alice", "age": "30", "score": "9.5"},
    {"name": "bob", "age": "25", "score": "7.0"},
    {"name": " Carol ", "age": "", "score": "8.25"},
]


def test_cast_int():
    out = typecast_column(ROWS, "age", "int")
    assert out[0]["age"] == "30"
    assert out[1]["age"] == "25"
    assert out[2]["age"] == ""  # empty passthrough


def test_cast_float():
    out = typecast_column(ROWS, "score", "float")
    assert out[0]["score"] == "9.5"
    assert out[2]["score"] == "8.25"


def test_cast_upper():
    out = typecast_column(ROWS, "name", "upper")
    assert out[0]["name"] == "ALICE"
    assert out[1]["name"] == "BOB"


def test_cast_lower():
    out = typecast_column(ROWS, "name", "lower")
    assert out[0]["name"] == "alice"


def test_cast_strip():
    out = typecast_column(ROWS, "name", "strip")
    assert out[2]["name"] == "Carol"


def test_cast_invalid_type_raises():
    with pytest.raises(ValueError, match="Unknown cast type"):
        typecast_column(ROWS, "age", "datetime")


def test_cast_bad_value_passthrough():
    rows = [{"age": "notanumber"}]
    out = typecast_column(rows, "age", "int")
    assert out[0]["age"] == "notanumber"


def test_cast_missing_column_ignored():
    out = typecast_column(ROWS, "nonexistent", "upper")
    assert out == ROWS


def test_does_not_mutate_original():
    original = [{"name": "Alice"}]
    typecast_column(original, "name", "upper")
    assert original[0]["name"] == "Alice"


def test_typecast_many():
    out = typecast_many(ROWS, {"name": "upper", "score": "float"})
    assert out[0]["name"] == "ALICE"
    assert out[0]["score"] == "9.5"
    assert out[0]["age"] == "30"  # untouched
