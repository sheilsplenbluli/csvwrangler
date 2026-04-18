import pytest
from csvwrangler.enrich import add_column, add_row_number


ROWS = [
    {"first": "Alice", "last": "Smith", "score": "10"},
    {"first": "Bob", "last": "Jones", "score": "20"},
    {"first": "Carol", "last": "White", "score": "30"},
]


def test_template_concat():
    result = add_column(ROWS, "full_name", "{first} {last}")
    assert result[0]["full_name"] == "Alice Smith"
    assert result[1]["full_name"] == "Bob Jones"


def test_template_missing_field():
    result = add_column(ROWS, "x", "{first}_{missing}")
    assert result[0]["x"] == "Alice_"


def test_template_does_not_mutate_original():
    result = add_column(ROWS, "tag", "person")
    assert "tag" not in ROWS[0]
    assert result[0]["tag"] == "person"


def test_math_add():
    result = add_column(ROWS, "double", "{score} * 2", mode="math")
    assert result[0]["double"] == "20.0"
    assert result[2]["double"] == "60.0"


def test_math_complex_expr():
    result = add_column(ROWS, "adj", "{score} + 5", mode="math")
    assert result[1]["adj"] == "25.0"


def test_math_bad_field_defaults_zero():
    result = add_column(ROWS, "val", "{nonexistent} + 1", mode="math")
    assert result[0]["val"] == "1.0"


def test_math_invalid_expr_returns_empty():
    result = add_column(ROWS, "bad", "{score} *** 2", mode="math")
    assert result[0]["bad"] == ""


def test_add_row_number_default():
    result = add_row_number(ROWS)
    assert result[0]["row_num"] == "1"
    assert result[2]["row_num"] == "3"


def test_add_row_number_custom_start():
    result = add_row_number(ROWS, start=0)
    assert result[0]["row_num"] == "0"


def test_add_row_number_custom_col():
    result = add_row_number(ROWS, col_name="idx")
    assert "idx" in result[0]
    assert "row_num" not in result[0]


def test_add_row_number_preserves_fields():
    result = add_row_number(ROWS)
    assert result[0]["first"] == "Alice"


def test_row_number_first_column():
    result = add_row_number(ROWS)
    assert list(result[0].keys())[0] == "row_num"
