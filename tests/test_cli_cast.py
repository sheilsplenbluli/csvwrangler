import csv
import io
import os
import tempfile
import pytest
from unittest.mock import patch
from csvwrangler.cli_cast import run


def _write_csv(path, rows):
    with open(path, 'w', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def sample_csv(tmp_path):
    p = tmp_path / 'data.csv'
    _write_csv(str(p), [{'name': 'alice', 'age': '30'}, {'name': 'bob', 'age': '25'}])
    return str(p)


def test_infer_only_prints_types(sample_csv, capsys):
    run([sample_csv, '--infer-only'])
    out = capsys.readouterr().out
    assert 'name: str' in out
    assert 'age: int' in out


def test_auto_cast_stdout(sample_csv, capsys):
    run([sample_csv])
    out = capsys.readouterr().out
    assert 'alice' in out
    assert '30' in out


def test_auto_cast_output_file(sample_csv, tmp_path):
    out_path = str(tmp_path / 'out.csv')
    run([sample_csv, '-o', out_path])
    assert os.path.exists(out_path)
    with open(out_path) as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    assert rows[0]['age'] == '30'


def test_cast_specific_columns(sample_csv, capsys):
    run([sample_csv, '--columns', 'age'])
    out = capsys.readouterr().out
    assert 'age' in out


def test_empty_file_exits_cleanly(tmp_path):
    p = tmp_path / 'empty.csv'
    p.write_text('name,age\n')
    run([str(p)])
