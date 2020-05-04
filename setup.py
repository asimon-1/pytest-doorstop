#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


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
    long_description=long_description,
    long_description_content_type="text/markdown",
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
