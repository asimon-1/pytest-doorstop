# TODO: Convert these tests from manual invocations to automated unit tests
import pytest
import doorstop
import pathlib
import git


class Dummy:
    pass


class MockRepo:
    def __init__(self, *args, **kwargs):
        self.head = Dummy()
        self.head.object = Dummy()
        self.head.object.hexsha = "d670460b4b4aece5915caf5c68d12f560a9fe3e4"


@pytest.fixture(autouse=True)
def setup_tests(testdir, monkeypatch):
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
