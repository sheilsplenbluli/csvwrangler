import pytest
from csvwrangler.hexbin import equal_width_bins, custom_width_bins


def _rows():
    return [
        {"id": "1", "val": "10"},
        {"id": "2", "val": "20"},
        {"id": "3", "val": "30"},
        {"id": "4", "val": "40"},
        {"id": "5", "val": "50"},
    ]


def test_equal_width_bins_adds_column():
    result = equal_width_bins(_rows(), "val", n_bins=5)
    assert all("val_eqbin" in r for r in result)


def test_equal_width_bins_correct_count():
    result = equal_width_bins(_rows(), "val", n_bins=5)
    labels = [r["val_eqbin"] for r in result]
    assert labels == ["1", "2", "3", "4", "5"]


def test_equal_width_bins_custom_dest():
    result = equal_width_bins(_rows(), "val", n_bins=2, dest="bucket")
    assert all("bucket" in r for r in result)


def test_equal_width_bins_two_buckets():
    result = equal_width_bins(_rows(), "val", n_bins=2)
    labels = [r["val_eqbin"] for r in result]
    # 10,20 -> bucket 1; 30,40,50 -> bucket 2
    assert labels[0] == "1"
    assert labels[-1] == "2"


def test_equal_width_bins_non_numeric_gets_fill():
    rows = [{"val": "abc"}, {"val": "10"}, {"val": ""}]
    result = equal_width_bins(rows, "val", n_bins=2, fill="N/A")
    assert result[0]["val_eqbin"] == "N/A"
    assert result[2]["val_eqbin"] == "N/A"


def test_equal_width_bins_all_same_value():
    rows = [{"val": "5"}, {"val": "5"}, {"val": "5"}]
    result = equal_width_bins(rows, "val", n_bins=3)
    assert all(r["val_eqbin"] == "1" for r in result)


def test_equal_width_bins_invalid_n_raises():
    with pytest.raises(ValueError):
        equal_width_bins(_rows(), "val", n_bins=0)


def test_equal_width_bins_does_not_mutate():
    original = _rows()
    copies = [dict(r) for r in original]
    equal_width_bins(original, "val", n_bins=3)
    assert original == copies


def test_custom_width_bins_adds_column():
    result = custom_width_bins(_rows(), "val", width=10)
    assert all("val_cwbin" in r for r in result)


def test_custom_width_bins_labels_contain_range():
    result = custom_width_bins(_rows(), "val", width=10)
    for r in result:
        label = r["val_cwbin"]
        assert "[" in label and "," in label and ")" in label


def test_custom_width_bins_custom_dest():
    result = custom_width_bins(_rows(), "val", width=20, dest="grp")
    assert all("grp" in r for r in result)


def test_custom_width_bins_non_numeric_fill():
    rows = [{"val": "hello"}, {"val": "20"}]
    result = custom_width_bins(rows, "val", width=5, fill="-")
    assert result[0]["val_cwbin"] == "-"


def test_custom_width_bins_invalid_width_raises():
    with pytest.raises(ValueError):
        custom_width_bins(_rows(), "val", width=0)


def test_custom_width_bins_does_not_mutate():
    original = _rows()
    copies = [dict(r) for r in original]
    custom_width_bins(original, "val", width=15)
    assert original == copies
