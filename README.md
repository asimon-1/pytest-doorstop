# pytest-doorstop


![image](https://img.shields.io/pypi/v/pytest-doorstop.svg%0A%20:target:%20https://pypi.org/project/pytest-doorstop%0A%20:alt:%20PyPI%20version)

![image](https://img.shields.io/pypi/pyversions/pytest-doorstop.svg%0A%20:target:%20https://pypi.org/project/pytest-doorstop%0A%20:alt:%20Python%20versions)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A pytest plugin for adding test results into doorstop items.

--------

## Table of Contents

- [Features](#features)
- [Usage](#usage)
- [Installation](#installation)
- [Contributing](#contributing)
- [License](#license)

--------

## Features

-   Save pytest results to corresponding Doorstop items
-   For each test, writes extended attributes for:
    - Most recent test result
    - Commit hash of most recent test run
    - Commit hash where of the most recent successful test run
-   Supports PASS, FAIL, SKIP, XFAIL, and XPASS results

| Test Outcome | Outcome Written | Update Last Run Commit? | Update Last Passed Commit? |
|:------------:|:---------------:|:-----------------------:|:--------------------------:|
|   PASS (.)   |      passed     |           Yes           |             Yes            |
|   FAIL (F)   |      failed     |           Yes           |             No             |
|   SKIP  (S)  |       None      |            No           |             No             |
|   XPASS (X)  |      xpass      |           Yes           |             Yes            |
|   XFAIL (x)  |      xfail      |           Yes           |             No             |

--------

## Usage

The plugin needs to locate the Doorstop items, either by specifying the path to the Doorstop Document or by the item prefix. The results will not be recorded unless the plugin is specifically invoked with a command line argument.

If your project looks like this:

```
py-myproject/
+-- myproject/
|   +-- __init__.py
|   └-- myproject.py
|
+-- tests/
|   +-- __init__.py
|   +-- test_a.py
|   └-- test_b.py
|
+-- doorstop/
|   +-- .doorstop.yml
|   +-- TST001.yml
|   +-- TST002.yml
|   +-- TST003.yml
|   +-- TST004.yml
|   +-- TST005.yml
|   └-- TST006.yml
|
+-- license.txt
+-- readme.md
+-- requirements.txt
+-- setup.py
```

Then you can invoke the plugin either like this:

```bash
$ pytest --doorstop_path doorstop
```

Or like this

```bash
$ pytest --doorstop_prefix TST
```

In case the path is not specified, the plugin will search for a document with the given prefix in the CWD and any immediate child directories. Giving both arguments may be helpful for projects with complex directory structures.

The first Doorstop item file which contains the the test function name will have the extended attributes added / updated according to the results of the test. For example:

```YAML
active: true
custom: 1
derived: false
header: ''
level: 4
links:
- REQ046: m9tMd0JM8O8idHTViqyYy1OL3dLiVY69bT63jNAGxPs=
normative: true
ref: test_yaml_encoding
reviewed: TIwopA6cvyjBMF17bB6p_RUNA7clNMaaEhXGYlAdpdk=
test_commit_last_passed: d670460b4b4aece5915caf5c68d12f560a9fe3e4
test_commit_latest: d670460b4b4aece5915caf5c68d12f560a9fe3e4
test_result_latest: passed
text: |
  Test that inputs can be loaded from a UTF-8 encoded YAML file.
```

--------

## Installation

You can install "pytest-doorstop" via
[pip](https://pypi.org/project/pip/) from
[PyPI](https://pypi.org/project):

```bash
$ pip install pytest-doorstop
```

### Dependencies

-   pytest
-   Doorstop
-   PyYAML
-   gitpython

--------

## Contributing

Contributions are very welcome, both in Issues and in Pull Requests. Tests can be run with
[tox](https://tox.readthedocs.io/en/latest/).

```bash
$ tox
```

If you encounter any problems, please [file an
issue](https://github.com/scuriosity/pytest-doorstop/issues) along with
a detailed description.

--------

## License

Distributed under the terms of the [GNU GPL
v3.0](http://www.gnu.org/licenses/gpl-3.0.txt) license,
"pytest-doorstop" is free and open source software

--------

This [pytest](https://github.com/pytest-dev/pytest) plugin was generated
with [Cookiecutter](https://github.com/audreyr/cookiecutter) along with
[@hackebrot](https://github.com/hackebrot)'s
[cookiecutter-pytest-plugin](https://github.com/pytest-dev/cookiecutter-pytest-plugin)
template.
