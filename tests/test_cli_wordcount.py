"""Integration tests for cli_wordcount.run."""
import csv
import io
import os
import tempfile

import pytest

from csvwrangler.cli_wordcount import run


def _write_csv(path: str, rows: list[dict], fieldnames: list[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def sample_csv(tmp_path):
    p = tmp_path / "sample.csv"
    _write_csv(
        str(p),
        [
            {"name": "Alice", "bio": "loves hiking and coding"},
            {"name": "Bob", "bio": "just coding"},
            {"name": "Carol", "bio": ""},
        ],
        ["name", "bio"],
    )
    return str(p)


def test_word_count_stdout(sample_csv, capsys):
    run([sample_csv, "bio", "--mode", "word"])
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    assert rows[0]["bio_word_count"] == "4"
    assert rows[1]["bio_word_count"] == "2"
    assert rows[2]["bio_word_count"] == "0"


def test_char_count_stdout(sample_csv, capsys):
    run([sample_csv, "bio", "--mode", "char"])
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    assert rows[0]["bio_char_count"] == str(len("loves hiking and coding"))


def test_custom_dest(sample_csv, capsys):
    run([sample_csv, "bio", "--mode", "word", "--dest", "wc"])
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    assert "wc" in rows[0]


def test_output_file(sample_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    run([sample_csv, "bio", "--mode", "word", "-o", out])
    with open(out, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert rows[0]["bio_word_count"] == "4"


def test_missing_file_exits():
    with pytest.raises(SystemExit):
        run(["nonexistent.csv", "bio"])


def test_bad_column_exits(sample_csv):
    with pytest.raises(SystemExit):
        run([sample_csv, "does_not_exist"])
