"""Tests for cli_sample.run."""
import csv
import io
import os
import tempfile

import pytest

from csvwrangler.cli_sample import run


def _write_csv(rows, fieldnames=None):
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="")
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    writer = csv.DictWriter(tmp, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    tmp.close()
    return tmp.name


ROWS = [{"name": f"person{i}", "score": str(i * 10)} for i in range(1, 11)]


def test_head_stdout(capsys):
    path = _write_csv(ROWS)
    try:
        run([path, "--head", "3"])
        out = capsys.readouterr().out
        reader = list(csv.DictReader(io.StringIO(out)))
        assert len(reader) == 3
        assert reader[0]["name"] == "person1"
    finally:
        os.unlink(path)


def test_tail_stdout(capsys):
    path = _write_csv(ROWS)
    try:
        run([path, "--tail", "2"])
        out = capsys.readouterr().out
        reader = list(csv.DictReader(io.StringIO(out)))
        assert len(reader) == 2
        assert reader[-1]["name"] == "person10"
    finally:
        os.unlink(path)


def test_n_sample_stdout(capsys):
    path = _write_csv(ROWS)
    try:
        run([path, "--n", "5", "--seed", "42"])
        out = capsys.readouterr().out
        reader = list(csv.DictReader(io.StringIO(out)))
        assert len(reader) == 5
    finally:
        os.unlink(path)


def test_frac_sample_stdout(capsys):
    path = _write_csv(ROWS)
    try:
        run([path, "--frac", "0.3", "--seed", "0"])
        out = capsys.readouterr().out
        reader = list(csv.DictReader(io.StringIO(out)))
        assert len(reader) == 3
    finally:
        os.unlink(path)


def test_output_file(capsys):
    path = _write_csv(ROWS)
    out_tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
    out_tmp.close()
    try:
        run([path, "--head", "4", "--output", out_tmp.name])
        with open(out_tmp.name, newline="") as f:
            reader = list(csv.DictReader(f))
        assert len(reader) == 4
    finally:
        os.unlink(path)
        os.unlink(out_tmp.name)


def test_no_mode_exits():
    path = _write_csv(ROWS)
    try:
        with pytest.raises(SystemExit):
            run([path])
    finally:
        os.unlink(path)
