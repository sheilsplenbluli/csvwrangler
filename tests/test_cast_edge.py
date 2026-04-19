import pytest
from csvwrangler.cast import infer_types, auto_cast, _infer_type


def test_negative_int_inferred():
    assert _infer_type(['-1', '-2', '3']) == 'int'


def test_negative_float_inferred():
    assert _infer_type(['-1.5', '2.0']) == 'float'


def test_leading_decimal_inferred_as_float():
    assert _infer_type(['.5', '.75']) == 'float'


def test_mixed_str_and_int_is_str():
    assert _infer_type(['1', 'abc']) == 'str'


def test_auto_cast_unknown_column_skipped():
    rows = [{'a': '1'}]
    result = auto_cast(rows, columns=['z'])
    assert result[0] == {'a': '1'}


def test_infer_types_float_column():
    rows = [{'score': '9.5'}, {'score': '8.0'}]
    types = infer_types(rows)
    assert types['score'] == 'float'


def test_auto_cast_preserves_all_columns():
    rows = [{'a': '1', 'b': 'hello', 'c': '3.14'}]
    result = auto_cast(rows)
    assert set(result[0].keys()) == {'a', 'b', 'c'}


def test_auto_cast_single_row():
    rows = [{'x': '42'}]
    result = auto_cast(rows)
    assert result[0]['x'] == '42'
