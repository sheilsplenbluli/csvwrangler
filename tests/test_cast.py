import pytest
from csvwrangler.cast import infer_types, auto_cast, _infer_type


def _rows(*dicts):
    return list(dicts)


def test_infer_int():
    assert _infer_type(['1', '2', '3']) == 'int'


def test_infer_float():
    assert _infer_type(['1.5', '2.0', '3.1']) == 'float'


def test_infer_str():
    assert _infer_type(['hello', 'world']) == 'str'


def test_infer_mixed_int_float_is_float():
    assert _infer_type(['1', '2.5']) == 'float'


def test_infer_empty_values_ignored():
    assert _infer_type(['', '1', '2']) == 'int'


def test_infer_all_empty_is_str():
    assert _infer_type(['', '']) == 'str'


def test_infer_types_returns_mapping():
    rows = [{'a': '1', 'b': 'hello'}, {'a': '2', 'b': 'world'}]
    result = infer_types(rows)
    assert result == {'a': 'int', 'b': 'str'}


def test_infer_types_empty_rows():
    assert infer_types([]) == {}


def test_auto_cast_int_column():
    rows = [{'x': '10'}, {'x': '20'}]
    result = auto_cast(rows)
    assert result[0]['x'] == '10'
    assert result[1]['x'] == '20'


def test_auto_cast_does_not_mutate_original():
    rows = [{'a': '1'}]
    auto_cast(rows)
    assert rows[0]['a'] == '1'


def test_auto_cast_specific_columns_only():
    rows = [{'a': '1', 'b': '2'}]
    result = auto_cast(rows, columns=['a'])
    assert 'b' in result[0]


def test_auto_cast_empty_value_preserved():
    rows = [{'a': ''}, {'a': '1'}]
    result = auto_cast(rows)
    assert result[0]['a'] == ''


def test_auto_cast_float_column():
    rows = [{'v': '1.5'}, {'v': '2.5'}]
    result = auto_cast(rows)
    assert result[0]['v'] == '1.5'
    assert result[1]['v'] == '2.5'


def test_auto_cast_empty_rows():
    assert auto_cast([]) == []
