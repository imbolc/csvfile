from __future__ import annotations

import csv
import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import (
    IO,
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Sequence,
    Set,
    Union,
)

__version__ = "3.2.0"


class Row(dict):
    """A dict with a dot-access"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__  # type:ignore
    __delattr__ = dict.__delitem__  # type:ignore


class load(list):
    def __init__(
        self,
        filename: Union[Path, str],
        *csvargs: Any,
        limit: Optional[int] = None,
        **csvkwargs: Any,
    ):
        super().__init__()
        self.path = Path(filename)
        self.csvargs = csvargs
        self.csvkwargs = csvkwargs
        with self.path.open() as f:
            reader = DictReader(f, *csvargs, **csvkwargs)
            self.header = reader.header
            for i, row in enumerate(reader):
                if limit is not None and i >= limit:
                    break
                self.append(row)

    def sync(self):
        if not self:
            return
        with self.path.open("w") as f:
            csv.writer(f, *self.csvargs, **self.csvkwargs).writerow(
                [h.raw for h in self.header]
            )
            w = writer(
                f,
                [h.type for h in self.header],
                *self.csvargs,
                **self.csvkwargs,
            )
            for row in self:
                vals = [row[h.name] for h in self.header]
                w.writerow(vals)

    def append(self, row: Dict[str, Any]):
        super().append(Row(row))

    def extend(self, rows: Iterable[Dict[str, Any]]):
        for row in rows:
            self.append(row)

    def insert(self, i, row):
        super().insert(i, Row(row))


class CellType(NamedTuple):
    name: str
    aliases: Set[Any]
    loads: Callable
    dumps: Callable

    @classmethod
    def get(cls, name: str) -> CellType:
        for type in TYPES:
            if type.name == name or name in type.aliases:
                return type
        raise TypeError(f"unknown cell type: {name}")


class Boolean:
    STR_MAP = {
        "true": True,
        "false": False,
        "t": True,
        "f": False,
        "1": True,
        "0": False,
        "y": True,
        "n": False,
        "yes": True,
        "no": False,
        "on": True,
        "off": False,
    }

    @classmethod
    def loads(cls, s: str) -> bool:
        try:
            return cls.STR_MAP[s.lower().strip()]
        except KeyError:
            raise ValueError(f"can't convert `{s}` into boolean")

    @classmethod
    def dumps(cls, val: bool) -> str:
        return str(bool(val)).lower()


TYPES = [
    CellType("str", {"s"}, str, str),
    CellType("bool", {"b", "boolean"}, Boolean.loads, Boolean.dumps),
    CellType("int", {"i"}, int, str),
    CellType("float", {"f"}, float, str),
    CellType("decimal", {"n"}, Decimal, str),
    CellType("date", {"d"}, date.fromisoformat, date.isoformat),
    CellType("datetime", {"t"}, datetime.fromisoformat, datetime.isoformat),
    CellType("json", {"j"}, json.loads, json.dumps),
]


class HeaderCell(NamedTuple):
    raw: str
    name: str
    type: CellType

    @classmethod
    def from_str(cls, raw: str) -> HeaderCell:
        parts = raw.rsplit(":", 1)
        if len(parts) == 2:
            name, type_name = [x.strip() for x in parts]
        else:
            name, type_name = (raw.strip(), "str")
        return cls(raw, name, CellType.get(type_name))


def reader(
    csvfile: Iterable,
    types=Sequence[CellType],
    dialect: str = "excel",
    **fmtparams: dict,
) -> Iterator[List[Any]]:
    for i, row in enumerate(csv.reader(csvfile, dialect, **fmtparams)):
        _check_row_length(i, row, types)
        yield [
            t.loads(s) if s.strip() or t.name == "str" else None
            for t, s in zip(types, row)
        ]


class TypedWriter:
    def __init__(self, csvfile, types, *args, **kwargs):
        self.row_num = 0
        self.types = types
        self._writer = csv.writer(csvfile, *args, **kwargs)

    def writerow(self, row: Sequence[Any]):
        _check_row_length(self.row_num, row, self.types)
        self._writer.writerow(
            [
                t.dumps(x) if x is not None else ""
                for t, x in zip(self.types, row)
            ]
        )


def writer(
    csvfile: IO,
    types=Sequence[CellType],
    dialect: str = "excel",
    **fmtparams: dict,
) -> TypedWriter:
    return TypedWriter(csvfile, types, dialect, **fmtparams)


class DictReader:
    def __init__(self, f: Iterable, dialect: str = "excel", **fmtparams):
        f = iter(f)
        self.header = self._read_header(f, dialect, **fmtparams)
        self.reader = reader(
            f, [x.type for x in self.header], dialect, **fmtparams
        )

    def _read_header(
        self, f: Iterable, dialect: str, **fmtparams
    ) -> List[HeaderCell]:
        reader = csv.reader(f, dialect, **fmtparams)
        try:
            row = next(reader)
        except StopIteration:
            raise StopIteration("Can't read csv headers")
        return [HeaderCell.from_str(x) for x in row]

    def __iter__(self):
        return self

    def __next__(self) -> Dict[str, Any]:
        vals = next(self.reader)
        return {h.name: v for h, v in zip(self.header, vals)}


def _check_row_length(row_num: int, row: Sequence, types: Sequence) -> None:
    if len(row) != len(types):
        raise ValueError(
            f"length of the row #{row_num} is {len(row)} "
            f"while you {len(types)} types provided"
        )
