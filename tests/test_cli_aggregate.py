import csv
import io
import os
import tempfile
import pytest
from unittest.mock import patch
from csvwrangler.cli_aggregate import run


def _write_csv(path: str, rows: list[dict], fieldnames: list[str]) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


ROWS = [
    {"dept": "eng", "name": "alice", "salary": "90000"},
    {"dept": "eng", "name": "bob", "salary": "80000"},
    {"dept": "hr", "name": "carol", "salary": "70000"},
]


def test_sum_stdout(capsys):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        path = f.name
    try:
        _write_csv(path, ROWS, ["dept", "name", "salary"])
        run([path, "--group-by", "dept", "--agg", "total:sum:salary"])
        out = capsys.readouterr().out
        assert "total" in out
        assert "170000" in out
    finally:
        os.unlink(path)


def test_count_stdout(capsys):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        path = f.name
    try:
        _write_csv(path, ROWS, ["dept", "name", "salary"])
        run([path, "--group-by", "dept", "--agg", "n:count:name"])
        out = capsys.readouterr().out
        assert "n" in out
        assert "2" in out
    finally:
        os.unlink(path)


def test_output_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as fin:
        in_path = fin.name
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as fout:
        out_path = fout.name
    try:
        _write_csv(in_path, ROWS, ["dept", "name", "salary"])
        run([in_path, "--group-by", "dept", "--agg", "total:sum:salary", "-o", out_path])
        with open(out_path) as f:
            content = f.read()
        assert "total" in content
    finally:
        os.unlink(in_path)
        os.unlink(out_path)


def test_bad_agg_spec_exits():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        path = f.name
    try:
        _write_csv(path, ROWS, ["dept", "name", "salary"])
        with pytest.raises(SystemExit):
            run([path, "--group-by", "dept", "--agg", "badspec"])
    finally:
        os.unlink(path)
