import json
from io import StringIO
from pathlib import Path

import pytest  # type: ignore

from csvfile import (
    Boolean,
    CellType,
    DictReader,
    HeaderCell,
    load,
    reader,
    writer,
)

PATH = Path("/tmp/csvfile_test.csv")
TEST_DATA = [
    {"language": "python", "created": 1991},
    {"language": "javascript", "created": 1995},
]
TEST_TEXT = "language,created:i\npython,1991\njavascript,1995\n"
TEST_FIELDNAMES = ["language", "created"]


def setup_function():
    PATH.unlink(missing_ok=True)


def save_test_text():
    PATH.write_text(TEST_TEXT)


def test_cell_type():
    assert CellType.get("s").name == "str"
    with pytest.raises(TypeError):
        CellType.get("foo")


def test_boolean():
    for s in ["tRue", "T", "1", "Y", "yEs", "On"]:
        assert Boolean.loads(s)
    for s in ["false", "f", "0", "n", "nO", "off"]:
        assert not Boolean.loads(s)
    with pytest.raises(ValueError):
        Boolean.loads("foo")


def test_headercell_typed():
    x = HeaderCell.from_str(" foo:bar :  j ")
    assert x.raw == " foo:bar :  j "
    assert x.name == "foo:bar"
    assert x.type == CellType.get("json")


def test_headercell_no_type():
    assert HeaderCell.from_str("foo").type.name == "str"


def test_headercell_wrong_type():
    with pytest.raises(TypeError):
        HeaderCell.from_str("foo:wrong")


def test_reader_row_length_mismatch():
    text = ["foo,1", "bar"]
    with pytest.raises(ValueError):
        list(reader(text, [CellType.get("s"), CellType.get("i")]))


def test_reader_success():
    text = ["foo,1", "bar,2"]
    data = list(reader(text, [CellType.get("s"), CellType.get("i")]))
    assert data == [["foo", 1], ["bar", 2]]


def test_reader_none():
    text = ["foo,1", ","]
    data = list(reader(text, [CellType.get("s"), CellType.get("i")]))
    assert data == [["foo", 1], ["", None]]


def test_writer_row_length_mismatch():
    file = StringIO()
    w = writer(file, [CellType.get("s"), CellType.get("i")])
    with pytest.raises(ValueError):
        w.writerow(["foo"])


def test_writer_success():
    file = StringIO()
    w = writer(file, [CellType.get("s"), CellType.get("i")])
    w.writerow(["foo", 1])
    assert file.getvalue() == "foo,1\r\n"


def test_writer_none():
    file = StringIO()
    w = writer(file, [CellType.get("b"), CellType.get("i")])
    w.writerow([None, None])
    assert file.getvalue() == ",\r\n"


def test_dictreader_success():
    text = ["name:s,num:i", "foo,1"]
    data = list(DictReader(text))
    assert data == [{"name": "foo", "num": 1}]


def test_dictreader_success_no_types():
    text = ["name,num", "foo,1"]
    data = list(DictReader(text))
    assert data == [{"name": "foo", "num": "1"}]


def test_dictreader_row_length_mismatch():
    text = ["name,num", "foo,1,2"]
    with pytest.raises(ValueError):
        list(DictReader(text))
    text = ["name,num", "foo"]
    with pytest.raises(ValueError):
        list(DictReader(text))


def test_dictreader_empty_file():
    f = StringIO()
    with pytest.raises(StopIteration):
        list(DictReader(f))


def test_dict_load():
    save_test_text()
    table = load(PATH)
    assert json.dumps(table) == json.dumps(TEST_DATA)


def test_dict_sync():
    save_test_text()
    table = load(PATH)
    table.sync()
    assert PATH.read_text() == TEST_TEXT


def test_update():
    save_test_text()
    table = load(PATH)
    table[1]["language"] = "js"
    table.append({"language": "rust", "created": 2010})
    table.sync()
    table = load(PATH)
    assert len(table) == 3
    assert table[1]["language"] == "js"
    assert table[2]["created"] == 2010
