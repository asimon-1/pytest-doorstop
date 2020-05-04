#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding="utf-8").read()


setup(
    name="pytest-doorstop",
    version="0.1.0",
    author="Andrew Simon",
    author_email="asimon1@protonmail.com",
    maintainer="Andrew Simon",
    maintainer_email="asimon1@protonmail.com",
    license="GNU GPL v3.0",
    url="https://github.com/scuriosity/pytest-doorstop",
    description="A pytest plugin for adding test results into doorstop items.",
    long_description=read("README.md"),
    py_modules=["pytest_doorstop"],
    python_requires=">=3.7",
    install_requires=["pytest>=3.5.0", "doorstop>=2", "PyYAML>=5" "gitpython>=3"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    entry_points={"pytest11": ["pytest_doorstop = pytest_doorstop"]},
)
