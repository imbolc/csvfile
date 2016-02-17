import os
import csv
import builtins


__version__ = '1.0.0'


class open(list):
    '''
    >>> filename = '/tmp/csvfile_test.csv'

    >>> csvfile = open(filename, fieldnames=['language', 'created'])
    >>> del csvfile[:]
    >>> csvfile.append({'language': 'python', 'created': 1991})
    >>> csvfile.append({'language': 'javascript', 'created': 1995})
    >>> csvfile.save()

    >>> csvfile = open(filename).load()
    >>> csvfile[0]['language']
    'python'

    >>> csvfile[1]['language'] = 'js'
    >>> csvfile.save()

    >>> csvfile = open(filename).load()
    >>> csvfile[1]['language']
    'js'
    '''

    def __init__(self, filename, *, fieldnames=None, encoding='utf-8'):
        super().__init__()
        self.filename = filename
        self.fieldnames = fieldnames
        self.encoding = encoding

    def load(self):
        with builtins.open(self.filename, 'rt', encoding=self.encoding) as f:
            reader = csv.DictReader(f, fieldnames=self.fieldnames)
            for row in reader:
                self.append(row)
            self.fieldnames = reader.fieldnames
        return self

    def save(self):
        with builtins.open(self.filename, 'wt', encoding=self.encoding) as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames,
                                    lineterminator=os.linesep)
            if self.fieldnames:
                writer.writeheader()
            writer.writerows(self)


if __name__ == "__main__":
    import doctest
    print(doctest.testmod())
