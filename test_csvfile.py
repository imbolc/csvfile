import json
from pathlib import Path

from csvfile import CSVFile, load

PATH = Path("/tmp/csvfile_test.csv")
TEST_DATA = [
    {"language": "python", "created": "1991"},
    {"language": "javascript", "created": "1995"},
]
TEST_TEXT = "language,created\npython,1991\njavascript,1995\n"
TEST_FIELDNAMES = ["language", "created"]


def setup_function():
    PATH.unlink(missing_ok=True)


def save_test_text():
    PATH.write_text(TEST_TEXT)


def test_creation():
    csvfile = CSVFile(PATH, fieldnames=TEST_FIELDNAMES)
    csvfile.extend(TEST_DATA)
    csvfile.sync()
    assert PATH.read_text() == TEST_TEXT


def test_load():
    save_test_text()
    csvfile = load(PATH)
    assert len(csvfile) == 2
    assert json.dumps(csvfile) == json.dumps(TEST_DATA)
    csvfile.sync()
    assert PATH.read_text() == TEST_TEXT


def test_change_file():
    save_test_text()
    csvfile = CSVFile(PATH).load()
    csvfile[1]["language"] = "js"
    csvfile.sync()
    csvfile = CSVFile(PATH).load()
    assert csvfile[1]["language"] == "js"
