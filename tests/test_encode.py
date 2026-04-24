import pytest
from csvwrangler.encode import onehot_encode, label_encode, encode_many


def _rows():
    return [
        {"name": "alice", "color": "red"},
        {"name": "bob",   "color": "blue"},
        {"name": "carol", "color": "red"},
        {"name": "dave",  "color": "green"},
    ]


def test_onehot_adds_columns():
    result = onehot_encode(_rows(), "color")
    assert "color_red" in result[0]
    assert "color_blue" in result[0]
    assert "color_green" in result[0]


def test_onehot_correct_values():
    result = onehot_encode(_rows(), "color")
    assert result[0]["color_red"] == "1"
    assert result[0]["color_blue"] == "0"
    assert result[1]["color_blue"] == "1"
    assert result[1]["color_red"] == "0"


def test_onehot_keeps_original_by_default():
    result = onehot_encode(_rows(), "color")
    assert "color" in result[0]


def test_onehot_drop_original():
    result = onehot_encode(_rows(), "color", drop_original=True)
    assert "color" not in result[0]


def test_onehot_custom_prefix():
    result = onehot_encode(_rows(), "color", prefix="c")
    assert "c_red" in result[0]
    assert "color_red" not in result[0]


def test_onehot_empty_rows():
    assert onehot_encode([], "color") == []


def test_onehot_does_not_mutate_original():
    rows = _rows()
    onehot_encode(rows, "color")
    assert "color_red" not in rows[0]


def test_label_encode_default_dest():
    result = label_encode(_rows(), "color")
    assert "color_encoded" in result[0]


def test_label_encode_values_are_integers():
    result = label_encode(_rows(), "color")
    # first appearance order: red=0, blue=1, green=2
    assert result[0]["color_encoded"] == "0"  # red
    assert result[1]["color_encoded"] == "1"  # blue
    assert result[2]["color_encoded"] == "0"  # red again
    assert result[3]["color_encoded"] == "2"  # green


def test_label_encode_custom_dest():
    result = label_encode(_rows(), "color", dest="col_id")
    assert "col_id" in result[0]
    assert "color_encoded" not in result[0]


def test_label_encode_custom_mapping():
    mapping = {"red": 10, "blue": 20, "green": 30}
    result = label_encode(_rows(), "color", mapping=mapping)
    assert result[0]["color_encoded"] == "10"
    assert result[1]["color_encoded"] == "20"


def test_label_encode_unknown_value_empty():
    mapping = {"red": 1}
    result = label_encode(_rows(), "color", mapping=mapping)
    assert result[1]["color_encoded"] == ""  # blue not in mapping


def test_label_encode_empty_rows():
    assert label_encode([], "color") == []


def test_encode_many_onehot():
    rows = [{"a": "x", "b": "p"}, {"a": "y", "b": "q"}]
    result = encode_many(rows, ["a", "b"], mode="onehot")
    assert "a_x" in result[0]
    assert "b_p" in result[0]


def test_encode_many_label():
    rows = [{"a": "x"}, {"a": "y"}, {"a": "x"}]
    result = encode_many(rows, ["a"], mode="label")
    assert result[0]["a_encoded"] == "0"
    assert result[1]["a_encoded"] == "1"
