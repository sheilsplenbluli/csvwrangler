"""Tests for csvwrangler/strcase.py"""

import pytest
from csvwrangler.strcase import (
    _to_snake, _to_camel, _to_pascal, _to_kebab,
    strcase_column, strcase_many,
)


def _rows():
    return [
        {'name': 'hello world', 'val': '1'},
        {'name': 'fooBar', 'val': '2'},
        {'name': 'MyVariableName', 'val': '3'},
        {'name': 'already-kebab', 'val': '4'},
        {'name': '', 'val': '5'},
    ]


def test_to_snake_spaces():
    assert _to_snake('hello world') == 'hello_world'


def test_to_snake_camel():
    assert _to_snake('fooBar') == 'foo_bar'


def test_to_snake_pascal():
    assert _to_snake('MyVariableName') == 'my_variable_name'


def test_to_snake_kebab():
    assert _to_snake('already-kebab') == 'already_kebab'


def test_to_camel_spaces():
    assert _to_camel('hello world') == 'helloWorld'


def test_to_camel_snake():
    assert _to_camel('foo_bar_baz') == 'fooBarBaz'


def test_to_pascal_basic():
    assert _to_pascal('hello world') == 'HelloWorld'


def test_to_pascal_snake():
    assert _to_pascal('my_variable_name') == 'MyVariableName'


def test_to_kebab_spaces():
    assert _to_kebab('hello world') == 'hello-world'


def test_to_kebab_camel():
    assert _to_kebab('fooBar') == 'foo-bar'


def test_strcase_column_snake():
    rows = _rows()
    result = strcase_column(rows, 'name', 'snake')
    assert result[0]['name'] == 'hello_world'
    assert result[1]['name'] == 'foo_bar'
    assert result[2]['name'] == 'my_variable_name'


def test_strcase_column_dest():
    rows = _rows()
    result = strcase_column(rows, 'name', 'camel', dest='name_camel')
    assert 'name_camel' in result[0]
    assert result[0]['name'] == 'hello world'  # original unchanged
    assert result[0]['name_camel'] == 'helloWorld'


def test_strcase_column_empty_passthrough():
    rows = _rows()
    result = strcase_column(rows, 'name', 'pascal')
    assert result[4]['name'] == ''


def test_strcase_column_does_not_mutate():
    rows = _rows()
    original = rows[0]['name']
    strcase_column(rows, 'name', 'snake')
    assert rows[0]['name'] == original


def test_strcase_column_unknown_mode_raises():
    with pytest.raises(ValueError, match='Unknown mode'):
        strcase_column(_rows(), 'name', 'title_case')


def test_strcase_many_applies_in_order():
    rows = [{'a': 'hello world', 'b': 'foo_bar'}]
    specs = [
        {'column': 'a', 'mode': 'pascal'},
        {'column': 'b', 'mode': 'camel'},
    ]
    result = strcase_many(rows, specs)
    assert result[0]['a'] == 'HelloWorld'
    assert result[0]['b'] == 'fooBar'


def test_strcase_many_with_dest():
    rows = [{'name': 'some value'}]
    specs = [{'column': 'name', 'mode': 'kebab', 'dest': 'slug'}]
    result = strcase_many(rows, specs)
    assert result[0]['slug'] == 'some-value'
    assert result[0]['name'] == 'some value'
