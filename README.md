csvfile
=======
A simple way of working with csv files.

You can use:

```python
data = csvfile.load("my-data.csv")
data[0]["field"] = "new value"
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

Typing
------

You also can provide a model based on `pydantic.BaseModel`. This will give you
types checking and conversion:

```python
>>> import csvfile, pydantic, decimal, datetime
>>> class Transaction(pydantic.BaseModel):
...     amount: decimal.Decimal
...     at: datetime.datetime
>>> table = csvfile.CSVFile("./transactions.csv", model=Transaction)
>>> table.append(Transaction(amount="10.5", at=datetime.datetime.now()))
>>> open("./transactions.csv").read()
'amount,at\n10.5,2020-03-11 14:13:31.087455\n'
>>> csvfile.load("./transactions.csv", model=Transaction)
[Transaction(amount=Decimal('10.5'), at=datetime.datetime(2020, 3, 11, 14, 13, 31, 87455))]
```

Tip: to annotate only a part of columns you can use
[pydantic.config.extra](https://pydantic-docs.helpmanual.io/usage/model_config/)
attribute:

```python
class Transaction(pydantic.BaseModel):
    ...
    class Config:
        extra = 'allow'
```

Running tests
-------------
    pip install -r requirements-dev.txt
    pytest
