import decimal
import json
from datetime import date, datetime
from io import StringIO

import pytest  # type: ignore

import typedcsv


def test_cell_type():
    assert typedcsv.CellType.get(str).name == "str"
    with pytest.raises(TypeError):
        typedcsv.CellType.get("foo")


def test_boolean():
    for s in ["tRue", "T", "1", "Y", "yEs", "On"]:
        assert typedcsv.Boolean.loads(s)
    for s in ["false", "f", "0", "n", "nO", "off"]:
        assert not typedcsv.Boolean.loads(s)
    with pytest.raises(ValueError):
        typedcsv.Boolean.loads("foo")


def test_reader_row_length_mismatch():
    text = ["foo,1", "bar"]
    with pytest.raises(ValueError):
        list(typedcsv.reader(text, ["s", "i"]))


def test_reader_success():
    text = ["foo,1", "bar,2"]
    data = list(typedcsv.reader(text, ["s", "i"]))
    assert data == [["foo", 1], ["bar", 2]]


def test_reader_aliases():
    text = ['foo,T,1,0.5,0.5,2020-03-28,2020-02-28T09:29,{"foo":1}']
    data = list(
        typedcsv.reader(
            text, [str, bool, int, float, decimal, date, datetime, json]
        )
    )
    assert data == [
        [
            "foo",
            True,
            1,
            0.5,
            decimal.Decimal("0.5"),
            date(2020, 3, 28),
            datetime(2020, 2, 28, 9, 29),
            {"foo": 1},
        ]
    ]


def test_writer_row_length_mismatch():
    file = StringIO()
    writer = typedcsv.writer(file, ["s", "i"])
    with pytest.raises(ValueError):
        writer.writerow(["foo"])


def test_writer_success():
    file = StringIO()
    writer = typedcsv.writer(file, ["s", "i"])
    writer.writerow(["foo", 1])
    assert file.getvalue() == "foo,1\r\n"
