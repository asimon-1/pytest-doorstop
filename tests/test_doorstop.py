import pytest


def test_pass():
    assert True


def test_fail():
    assert False


@pytest.mark.skip()
def test_skip():
    assert False


@pytest.mark.xfail
def test_xfail():
    assert False


@pytest.mark.xfail
def test_xpass():
    assert True
