csvfile
=======
A simple way of working with csv files.

You can use:

```python
data = csvfile.load("my-data.csv")
data[0].field = "new value"
data.sync()
```

Instead of:

```python
data = []
with open("my-data.csv") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        data.append(row)

data[0]["field"] = "new value"

with open("my-data.csv, "w") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
```

Also you can declaratively define types in a table's header:

```python
>>> print(open("/tmp/csvfile_test.csv").read())
language,created:i
python,1991
js,1995
rust,2010

>>> pprint(csvfile.load("/tmp/csvfile_test.csv"))
[{'created': 1991, 'language': 'python'},
 {'created': 1995, 'language': 'js'},
 {'created': 2010, 'language': 'rust'}]
```

Notice, that `created` is automatically converted into integer as we typed it in
the header as `created:i`.


Built-in types
--------------

| Type     | Alias | Comment                                                                                                                                                                                                     |
|----------|-------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| str      | s     | default, if no type specified                                                                                                                                                                               |
| bool     | b     | `reader` can understand next pairs as `True / False` case-insensitevely: `true / false`, `t / f`, `1 / 0`, `y / n`, `yes / no`, `on / off`, but the `writer` will always stringify them into `true / false` |
| int      | i     |                                                                                                                                                                                                             |
| float    | f     |                                                                                                                                                                                                             |
| decimal  | n     |                                                                                                                                                                                                             |
| date     | d     | ISO 8601, YYYY-MM-DD                                                                                                                                                                                        |
| datetime | t     | ISO 8601, YYYY-MM-DDTHH:MM:SS.ffffff                                                                                                                                                                        |
| json     | j     |                                                                                                                                                                                                             |

Empty cells will become `None` for any type except of `str`.
As in case of `str` there's no way to distinguish it from an empty string.


API
---
The api consists in a single function `load` with the signature:

```python
table = load(
    filename: Union[Path, str],   # the file should exist and contain headers
    *csvargs: Any,                # `*args` for the standard `csv.reader`
    limit: Optional[int] = None,  # maximum number of rows to read
    **csvkwargs: Any,             # `**fmtparams` for the standard `csv.reader`
)
```

The returned object has a `list` interface with an additional `sync` method to
save changes back into the file.



Running tests
-------------
    pip install -r requirements-dev.txt
    pytest
