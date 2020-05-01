"""Test the pytest-doorstop plugin."""
import pathlib

import git
import pytest
import yaml


class Dummy:
    """Attribute Container."""

    pass


class MockRepo:
    """Mock for git.Repo."""

    def __init__(self, *args, **kwargs):
        """Mock for git.Repo().head.object.hexsha."""
        self.head = Dummy()
        self.head.object = Dummy()
        self.head.object.hexsha = "d670460b4b4aece5915caf5c68d12f560a9fe3e4"


@pytest.fixture(autouse=True)
def setup_tests(testdir, monkeypatch):
    """Provide mock return values and example tests to run against."""
    monkeypatch.setattr(git, "Repo", MockRepo, raising=True)
    monkeypatch.setattr(
        pathlib.Path, "cwd", lambda: str(testdir),
    )
    testdir.copy_example("tests/example")
    testdir.makepyfile(
        """
import pytest

def test_pass():
    '''PASS

    Plugin should update the following attributes of the doorstop item.

        - test_commit_last_passed: <current git hash>
        - test_commit_latest: <current git hash>
        - test_result_latest: passed

    '''
    assert True


def test_fail():
    '''FAIL

    Plugin should update the following attributes of the doorstop item.


        - test_commit_latest: <current git hash>
        - test_result_latest: failed

    Plugin should not update the following attributes of the doorstop item.

        - test_commit_last_passed: <previous git hash>

    '''
    assert False


@pytest.mark.skip()
def test_skip():
    '''SKIP

    Plugin should not update the following attributes of the doorstop item.

        - test_commit_last_passed
        - test_commit_latest
        - test_result_latest

    '''
    assert False


@pytest.mark.xfail
def test_xfail():
    '''XFAIL

    Plugin should update the following attributes of the doorstop item.


        - test_commit_latest: <current git hash>
        - test_result_latest: xfail

    Plugin should not update the following attributes of the doorstop item.

        - test_commit_last_passed: <previous git hash>

    '''
    assert False


@pytest.mark.xfail
def test_xpass():
    '''XPASS

        Plugin should update the following attributes of the doorstop item.


        - test_commit_latest: <current git hash>
        - test_result_latest: xpass

    Plugin should not update the following attributes of the doorstop item.

        - test_commit_last_passed: <previous git hash>

    '''
    assert True
"""
    )


def read_file(testdir, filename):
    """Export the given test doorstop yaml file as dict."""
    path = pathlib.Path(str(testdir)).joinpath("TstPlan").resolve().joinpath(filename)
    with path.open("r") as f:
        contents = yaml.safe_load(f)
    return contents


def test_example_tests(testdir):
    """Make sure the base tests run as expected."""
    result = testdir.runpytest()
    result.assert_outcomes(passed=1, failed=1, skipped=1, xpassed=1, xfailed=1)


def test_example_tests_with_prefix(testdir):
    """Check that the plugin can find the document specified by a prefix."""
    result = testdir.runpytest("--doorstop_prefix", "TST")
    result.assert_outcomes(passed=1, failed=1, skipped=1, xpassed=1, xfailed=1)


def test_example_tests_with_path(testdir):
    """Check that the plugin can find the document specified by a path."""
    path = str(pathlib.Path(str(testdir)).joinpath("TstPlan").resolve())
    result = testdir.runpytest("--doorstop_path", path)
    result.assert_outcomes(passed=1, failed=1, skipped=1, xpassed=1, xfailed=1)


def test_pass_updates_attributes(testdir):
    """Check that a passing test has its Doorstop attributes updated."""
    testdir.runpytest("--doorstop_prefix", "TST")
    yaml_contents = read_file(testdir, "TST0001.yml")
    assert (
        yaml_contents["test_commit_last_passed"]
        == "d670460b4b4aece5915caf5c68d12f560a9fe3e4"
    )
    assert (
        yaml_contents["test_commit_latest"]
        == "d670460b4b4aece5915caf5c68d12f560a9fe3e4"
    )
    assert yaml_contents["test_result_latest"] == "passed"


def test_fail_updates_attributes(testdir):
    """Check that a failing test has its Doorstop attributes updated."""
    testdir.runpytest("--doorstop_prefix", "TST")
    yaml_contents = read_file(testdir, "TST0002.yml")
    assert "test_commit_last_passed" not in yaml_contents
    assert (
        yaml_contents["test_commit_latest"]
        == "d670460b4b4aece5915caf5c68d12f560a9fe3e4"
    )
    assert yaml_contents["test_result_latest"] == "failed"


def test_skip_updates_attributes(testdir):
    """Check that a skipped test does not have its Doorstop attributes updated."""
    testdir.runpytest("--doorstop_prefix", "TST")
    yaml_contents = read_file(testdir, "TST0003.yml")
    assert "test_commit_last_passed" not in yaml_contents
    assert "test_commit_latest" not in yaml_contents
    assert "test_result_latest" not in yaml_contents


def test_xfail_updates_attributes(testdir):
    """Check that an xfailing test has its Doorstop attributes updated."""
    testdir.runpytest("--doorstop_prefix", "TST")
    yaml_contents = read_file(testdir, "TST0004.yml")
    assert "test_commit_last_passed" not in yaml_contents
    assert (
        yaml_contents["test_commit_latest"]
        == "d670460b4b4aece5915caf5c68d12f560a9fe3e4"
    )
    assert yaml_contents["test_result_latest"] == "xfail"


def test_xpass_updates_attributes(testdir):
    """Check that an xpassing test has its Doorstop attributes updated."""
    testdir.runpytest("--doorstop_prefix", "TST")
    yaml_contents = read_file(testdir, "TST0005.yml")
    assert "test_commit_last_passed" not in yaml_contents
    assert (
        yaml_contents["test_commit_latest"]
        == "d670460b4b4aece5915caf5c68d12f560a9fe3e4"
    )
    assert yaml_contents["test_result_latest"] == "xpass"


def test_verbose(testdir):
    """Check that the verbose option adds more information to the output."""
    result = testdir.runpytest("--verbose", "--doorstop_prefix", "TST")
    result.stdout.fnmatch_lines(
        [
            "Writing outcome (passed) for doorstop item *\\TstPlan\\TST0001.yml",
            "Writing outcome (failed) for doorstop item *\\TstPlan\\TST0002.yml",
            "Writing outcome (xfail) for doorstop item *\\TstPlan\\TST0004.yml",
            "Writing outcome (xpass) for doorstop item *\\TstPlan\\TST0005.yml",
        ]
    )


def test_missing_item(testdir):
    """Check that tests without a Doorstop item are handled correctly."""
    testdir.makepyfile(
        """
def test_missing():
    assert True
"""
    )
    result = testdir.runpytest("--doorstop_prefix", "TST")
    assert "Writing outcome" not in result.stdout.str()

    result_verbose = testdir.runpytest("--verbose", "--doorstop_prefix", "TST")
    result_verbose.stdout.fnmatch_lines(
        ["Could not locate a Doorstop item for test_missing_item.py::test_missing"]
    )
