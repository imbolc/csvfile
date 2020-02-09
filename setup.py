#!/usr/bin/env python
import os
import sys

from setuptools import setup

import csvfile as mod

if sys.argv[-1] == "publish":
    os.system("python setup.py bdist_wheel")
    os.system("python -m twine upload dist/*")
    sys.exit(0)


with open("README.rst", "rt") as f:
    readme = f.read()


setup(
    name=mod.__name__,
    url="https://github.com/imbolc/%s" % mod.__name__,
    version=mod.__version__,
    description=readme.split("===\n")[1].strip().split("\n\n")[0],
    long_description=readme,
    py_modules=[mod.__name__],
    author="Imbolc",
    author_email="imbolc@imbolc.name",
    license="ISC",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
)
