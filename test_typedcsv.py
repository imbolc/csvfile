from io import StringIO

import pytest  # type: ignore

import typedcsv


def test_reader_row_length_mismatch():
    text = ["foo,1", "bar"]
    with pytest.raises(ValueError):
        list(typedcsv.reader(text, ["s", "i"]))


def test_reader_success():
    text = ["foo,1", "bar,2"]
    data = list(typedcsv.reader(text, ["s", "i"]))
    assert data == [["foo", 1], ["bar", 2]]


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
