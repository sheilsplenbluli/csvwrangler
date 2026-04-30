"""Integration tests for csvwrangler/cli_strcase.py"""

import csv
import io
import os
import tempfile
from unittest.mock import patch

import pytest

from csvwrangler.cli_strcase import run


def _write_csv(rows, path):
    if not rows:
        return
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


SAMPLE = [
    {'label': 'hello world', 'score': '10'},
    {'label': 'fooBar', 'score': '20'},
    {'label': 'MyVariableName', 'score': '30'},
]


def test_snake_stdout(capsys):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        tmp = f.name
    try:
        _write_csv(SAMPLE, tmp)
        run([tmp, 'label', 'snake'])
        captured = capsys.readouterr()
        assert 'hello_world' in captured.out
        assert 'foo_bar' in captured.out
        assert 'my_variable_name' in captured.out
    finally:
        os.unlink(tmp)


def test_camel_stdout(capsys):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        tmp = f.name
    try:
        _write_csv(SAMPLE, tmp)
        run([tmp, 'label', 'camel'])
        captured = capsys.readouterr()
        assert 'helloWorld' in captured.out
    finally:
        os.unlink(tmp)


def test_dest_column(capsys):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        tmp = f.name
    try:
        _write_csv(SAMPLE, tmp)
        run([tmp, 'label', 'pascal', '--dest', 'label_pascal'])
        captured = capsys.readouterr()
        assert 'label_pascal' in captured.out
        assert 'hello world' in captured.out  # original preserved
    finally:
        os.unlink(tmp)


def test_output_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        tmp_in = f.name
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        tmp_out = f.name
    try:
        _write_csv(SAMPLE, tmp_in)
        run([tmp_in, 'label', 'kebab', '--output', tmp_out])
        with open(tmp_out, newline='', encoding='utf-8') as fh:
            rows = list(csv.DictReader(fh))
        assert rows[0]['label'] == 'hello-world'
    finally:
        os.unlink(tmp_in)
        os.unlink(tmp_out)


def test_missing_file_exits():
    with pytest.raises(SystemExit):
        run(['nonexistent.csv', 'label', 'snake'])


def test_bad_column_exits():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        tmp = f.name
    try:
        _write_csv(SAMPLE, tmp)
        with pytest.raises(SystemExit):
            run([tmp, 'nonexistent_col', 'snake'])
    finally:
        os.unlink(tmp)
