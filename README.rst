csvfile
=======
A little wrapper around reading and writing of csv file.

You can use:

.. code-block:: python

    data = csvfile.load("my-data.csv")
    data[0]["field"] = "new value"
    data.save()


Instead of:

.. code-block:: python

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
