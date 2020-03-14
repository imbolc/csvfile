from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Sequence, Type, Union

__version__ = "2.1.1"


if TYPE_CHECKING:
    import pydantic


def load(
    filename: Union[Path, str],
    *,
    model: Optional[Type[pydantic.BaseModel]] = None,
    fieldnames: Optional[Sequence[str]] = None,
    encoding: str = "utf-8",
) -> CSVFile:
    return CSVFile(
        filename, model=model, fieldnames=fieldnames, encoding=encoding
    ).load()


class CSVFile(list):
    def __init__(
        self,
        filename: Union[Path, str],
        *,
        model: Optional[Type[pydantic.BaseModel]] = None,
        fieldnames: Optional[Sequence[str]] = None,
        encoding: str = "utf-8",
    ):
        super().__init__()
        self.path = Path(filename)
        if fieldnames and model:
            raise ValueError(
                "Passing both `model` and `fieldnames` doesn't make sense"
            )
        self.encoding = encoding
        self.model = model
        self.fieldnames = (
            list(model.__fields__.keys()) if model else fieldnames
        )

    def load(self) -> CSVFile:
        self.clear()
        if not self.path.is_file():
            return self
        with self.path.open(encoding=self.encoding) as f:
            reader = csv.DictReader(f)
            for row in reader:
                obj = self.model(**row) if self.model else row
                self.append(obj)
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
            writer.writeheader()
            writer.writerows(dict(x) for x in self)


if __name__ == "__main__":
    import doctest

    print(doctest.testmod())
