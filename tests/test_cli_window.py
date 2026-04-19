import csv
import io
import os
import tempfile
import pytest
from unittest.mock import patch
from csvwrangler.cli_window import run


def _write_csv(rows, path):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


@pytest.fixture
def sample_csv(tmp_path):
    p = tmp_path / "data.csv"
    _write_csv([{"x": str(i)} for i in range(1, 6)], p)
    return str(p)


def test_rolling_mean_stdout(sample_csv, capsys):
    run([sample_csv, "--col", "x", "--func", "mean", "--window", "2"])
    out = capsys.readouterr().out
    rows = list(csv.DictReader(io.StringIO(out)))
    assert "x_rolling_mean" in rows[0]
    assert rows[0]["x_rolling_mean"] == "1.0"
    assert rows[1]["x_rolling_mean"] == "1.5"


def test_rolling_sum_stdout(sample_csv, capsys):
    run([sample_csv, "--col", "x", "--func", "sum", "--window", "3"])
    out = capsys.readouterr().out
    rows = list(csv.DictReader(io.StringIO(out)))
    assert rows[2]["x_rolling_sum"] == "6.0"


def test_output_file(sample_csv, tmp_path):
    out_path = str(tmp_path / "out.csv")
    run([sample_csv, "--col", "x", "--func", "max", "--window", "2", "--output", out_path])
    assert os.path.exists(out_path)
    with open(out_path) as f:
        rows = list(csv.DictReader(f))
    assert "x_rolling_max" in rows[0]


def test_custom_dest(sample_csv, capsys):
    run([sample_csv, "--col", "x", "--func", "min", "--window", "1", "--dest", "mymin"])
    out = capsys.readouterr().out
    rows = list(csv.DictReader(io.StringIO(out)))
    assert "mymin" in rows[0]


def test_bad_column_exits(sample_csv):
    with pytest.raises(SystemExit):
        run([sample_csv, "--col", "nonexistent", "--func", "mean", "--window", "2"])


def test_bad_window_exits(sample_csv):
    with pytest.raises(SystemExit):
        run([sample_csv, "--col", "x", "--func", "mean", "--window", "0"])
