"""Plug to record test results in a Doorstop document."""
import pathlib

import git
import pytest
import yaml


def pytest_addoption(parser):
    """Add parser argument for doorstop document."""
    group = parser.getgroup("doorstop", "mark doorstop items with test results")
    group._addoption(
        "--doorstop_document",
        action="store",
        dest="doorstop_document",
        type=str,
        default=None,
        help="Location of the doorstop items",
    )


def get_commit_hash():
    """Return the full git hash for the current commit."""
    repo = git.Repo(search_parent_directories=True)
    return repo.head.object.hexsha


def get_document(config):
    """Convert commandline argument to a pathlib object."""
    if config.getoption("doorstop_document"):
        return pathlib.Path(config.getoption("doorstop_document"))
    return None


def get_doorstop_item(nodeid, document):
    """Search for the doorstop item that contains the test."""
    # TODO: Requires that the test function name be unique. Add in filename too?
    # TODO: Incorporate new array behavior
    for path in document.iterdir():
        if nodeid.split("::")[-1] in path.read_text():
            # TODO: Is reading from yaml more appropriate?
            return path


def record_outcome(doorstop_item, outcome, commit_hash, xfail):
    """Write the outcome to the doorstop item."""
    with doorstop_item.open("r") as f:
        contents = yaml.safe_load(f)
    contents["test_commit_latest"] = commit_hash
    if not xfail:
        contents["test_result_latest"] = outcome
        if outcome == "passed":
            contents["test_commit_last_passed"] = commit_hash
    else:
        if outcome == "skipped":
            contents["test_result_latest"] = "xfail"
        elif outcome == "passed":
            contents["test_result_latest"] = "xpass"
    with doorstop_item.open("w") as f:
        yaml.safe_dump(contents, f)


def pytest_report_teststatus(report, config):
    """Collect test status and record in the doorstop item if appropriate."""
    document = get_document(config)
    if document:
        if report.when == "call":
            doorstop_item = get_doorstop_item(report.nodeid, document)
            xfail = "xfail" in report.keywords
            if doorstop_item:
                commit_hash = get_commit_hash()  # TODO: Only call this once per session
                record_outcome(doorstop_item, report.outcome, commit_hash, xfail)
