import csv
import io
import os
import tempfile
import pytest
from unittest.mock import patch
from csvwrangler.cli_typecast import run


def _write_csv(path, rows, fieldnames):
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def sample_csv(tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(
        p,
        [{"name": "alice", "age": "30"}, {"name": "bob", "age": "25"}],
        ["name", "age"],
    )
    return str(p)


def test_cast_upper_stdout(sample_csv, capsys):
    run([sample_csv, "--cast", "name:upper"])
    out = capsys.readouterr().out
    assert "ALICE" in out
    assert "BOB" in out


def test_cast_int_stdout(sample_csv, capsys):
    run([sample_csv, "--cast", "age:int"])
    out = capsys.readouterr().out
    assert "30" in out


def test_cast_output_file(sample_csv, tmp_path):
    out_path = str(tmp_path / "out.csv")
    run([sample_csv, "--cast", "name:upper", "-o", out_path])
    with open(out_path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert rows[0]["name"] == "ALICE"


def test_bad_cast_spec_exits(sample_csv):
    with pytest.raises(SystemExit):
        run([sample_csv, "--cast", "nameUPPER"])


def test_unknown_cast_type_exits(sample_csv):
    with pytest.raises(SystemExit):
        run([sample_csv, "--cast", "name:datetime"])
