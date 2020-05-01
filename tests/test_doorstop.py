# TODO: Convert these tests from manual invocations to automated unit tests
import pytest


def test_pass():
    """PASS

    Plugin should update the following attributes of the doorstop item.

        - test_commit_last_passed: <current git hash>
        - test_commit_latest: <current git hash>
        - test_result_latest: passed

    """
    assert True


def test_fail():
    """FAIL

    Plugin should update the following attributes of the doorstop item.


        - test_commit_latest: <current git hash>
        - test_result_latest: failed

    Plugin should not update the following attributes of the doorstop item.

        - test_commit_last_passed: <previous git hash>

    """
    assert False


@pytest.mark.skip()
def test_skip():
    """SKIP

    Plugin should not update the following attributes of the doorstop item.

        - test_commit_last_passed
        - test_commit_latest
        - test_result_latest

    """
    assert False


@pytest.mark.xfail
def test_xfail():
    """XFAIL

    Plugin should update the following attributes of the doorstop item.


        - test_commit_latest: <current git hash>
        - test_result_latest: xfail

    Plugin should not update the following attributes of the doorstop item.

        - test_commit_last_passed: <previous git hash>

    """
    assert False


@pytest.mark.xfail
def test_xpass():
    """XPASS

        Plugin should update the following attributes of the doorstop item.


        - test_commit_latest: <current git hash>
        - test_result_latest: xpass

    Plugin should not update the following attributes of the doorstop item.

        - test_commit_last_passed: <previous git hash>

    """
    assert True
