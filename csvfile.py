from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Optional, Sequence, Union

__version__ = "2.0.0"


def load(
    filename: Union[Path, str],
    fieldnames: Optional[Sequence[str]] = None,
    *,
    encoding: str = "utf-8",
) -> CSVFile:
    return CSVFile(filename, fieldnames, encoding=encoding).load()


class CSVFile(list):
    def __init__(
        self,
        filename: Union[Path, str],
        fieldnames: Optional[Sequence[str]] = None,
        *,
        encoding: str = "utf-8",
    ):
        super().__init__()
        self.path = Path(filename)
        self.fieldnames = fieldnames
        self.encoding = encoding

    def load(self) -> CSVFile:
        self.clear()
        if not self.path.is_file():
            return self
        with self.path.open(encoding=self.encoding) as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                self.append(row)
            self.fieldnames = reader.fieldnames
        return self

    def sync(self):
        if not self:
            return
        if not self.fieldnames:
            self.fieldnames = list(self[0].keys())
        with self.path.open("w", encoding=self.encoding) as f:
            writer = csv.DictWriter(
                f, fieldnames=self.fieldnames, lineterminator=os.linesep
            )
            if self.fieldnames:
                writer.writeheader()
            writer.writerows(self)


if __name__ == "__main__":
    import doctest

    print(doctest.testmod())
