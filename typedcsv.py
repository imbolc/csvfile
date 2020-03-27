from __future__ import annotations

import csv
import json
from datetime import date, datetime
from decimal import Decimal
from typing import IO, Any, Callable, Iterable, List, NamedTuple, Sequence, Set


class CellType(NamedTuple):
    name: str
    aliases: Set[str]
    loads: Callable
    dumps: Callable

    @classmethod
    def get(cls, name: str) -> CellType:
        for type in TYPES:
            if type.name == name or name in type.aliases:
                return type
        raise TypeError(f"Unknown cell type: {name}")


TYPES = [
    CellType("str", {"s"}, str, str),
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
        """
        >>> x = HeaderCell.from_str(" foo:bar :  j ")
        >>> x.raw == " foo:bar :  j "
        True
        >>> x.name == "foo:bar"
        True
        >>> x.type == CellType.get("json")
        True

        >>> HeaderCell.from_str("foo").type == CellType.get("str")
        True

        >>> HeaderCell.from_str("foo:wrong")
        Traceback (most recent call last):
            ...
        TypeError: Unknown cell type: wrong
        """
        parts = raw.rsplit(":", 1)
        if len(parts) == 2:
            name, type_name = [x.strip() for x in parts]
        else:
            name, type_name = (raw.strip(), "str")
        return cls(raw, name, CellType.get(type_name))


def reader(
    csvfile: Iterable,
    types=Sequence[str],
    dialect: str = "excel",
    **fmtparams: dict,
) -> Iterable[List[Any]]:
    cell_types = [CellType.get(t) for t in types]
    len_types = len(cell_types)
    for i, row in enumerate(csv.reader(csvfile, dialect, **fmtparams)):
        if len(row) != len_types:
            raise ValueError(
                f"Length of the row #{i} is {len(row)} "
                f"while you {len_types} types provided"
            )
        yield [t.loads(s) for t, s in zip(cell_types, row)]


class TypedWriter:
    def __init__(self, csvfile, types, *args, **kwargs):
        self.row_num = 0
        self.types = [CellType.get(t) for t in types]
        self._writer = csv.writer(csvfile, *args, **kwargs)

    def writerow(self, row: Sequence[Any]):
        _check_row_length(self.row_num, row, self.types)
        self._writer.writerow([t.dumps(x) for t, x in zip(self.types, row)])

    def writerows(self, rows: Sequence[Sequence[Any]]):
        for row in rows:
            self.writerow(row)


def writer(
    csvfile: IO,
    types=Sequence[str],
    dialect: str = "excel",
    **fmtparams: dict,
) -> TypedWriter:
    return TypedWriter(csvfile, types, dialect, **fmtparams)


def _check_row_length(row_num: int, row: Sequence, types: Sequence) -> None:
    if len(row) != len(types):
        raise ValueError(
            f"Length of the row #{row_num} is {len(row)} "
            f"while you {len(types)} types provided"
        )


if __name__ == "__main__":
    import doctest

    print(doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE))
