import json
from pathlib import Path

from pydantic import BaseModel

from csvfile import CSVFile, load

PATH = Path("/tmp/csvfile_test.csv")
TEST_DATA = [
    {"language": "python", "created": "1991"},
    {"language": "javascript", "created": "1995"},
]
TEST_TEXT = "language,created\npython,1991\njavascript,1995\n"
TEST_FIELDNAMES = ["language", "created"]


class Model(BaseModel):
    language: str
    created: int


def setup_function():
    PATH.unlink(missing_ok=True)


def save_test_text():
    PATH.write_text(TEST_TEXT)


def test_dict_create():
    table = CSVFile(PATH, fieldnames=TEST_FIELDNAMES)
    table.extend(TEST_DATA)
    table.sync()
    assert PATH.read_text() == TEST_TEXT


def test_dict_load():
    save_test_text()
    table = load(PATH)
    assert json.dumps(table) == json.dumps(TEST_DATA)


def test_dict_sync():
    save_test_text()
    table = load(PATH)
    table.sync()
    assert PATH.read_text() == TEST_TEXT


def test_dict_update():
    save_test_text()
    table = CSVFile(PATH).load()
    table[1]["language"] = "js"
    table.append({"language": "rust", "created": 2010})
    table.sync()
    table = CSVFile(PATH).load()
    assert len(table) == 3
    assert table[1]["language"] == "js"
    assert table[2]["language"] == "rust"


def test_model_create():
    data = [Model(**x) for x in TEST_DATA]
    table = CSVFile(PATH, model=Model)
    table.extend(data)
    table.sync()
    assert PATH.read_text() == TEST_TEXT


def test_model_load():
    save_test_text()
    table = load(PATH, model=Model)
    assert len(table) == 2
    assert table[0].language == "python"
    assert table[0].created == 1991


def test_model_sync():
    save_test_text()
    table = load(PATH, model=Model)
    table.sync()
    assert PATH.read_text() == TEST_TEXT


def test_model_update():
    save_test_text()
    table = load(PATH, model=Model)
    table[1].language = "js"
    table.append(Model(language="rust", created=2010))
    table.sync()

    table = load(PATH, model=Model)
    assert len(table) == 3
    assert table[1] == Model(language="js", created=1995)
    assert table[2] == Model(language="rust", created=2010)
