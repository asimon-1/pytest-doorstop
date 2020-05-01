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


def get_commit_hash() -> str:
    """Return the full git hash for the current commit."""
    repo = git.Repo(search_parent_directories=True)
    return repo.head.object.hexsha


def get_document(config) -> pathlib.Path:
    """Convert commandline argument to a pathlib object."""
    # TODO: Use he doorstop API to find this: doorstop.build().find_document(docprefix)
    doorstop_document = config.getoption("doorstop_document")
    if doorstop_document:
        return pathlib.Path(doorstop_document)
    raise RuntimeError(f"Could not locate the Doorstop document {doorstop_document}")


def get_doorstop_item(nodeid: str, document: pathlib.Path) -> pathlib.Path:
    """Search for the doorstop item that contains the test."""
    # TODO: Use the doorstop API to find this --> document.items
    # TODO: Implement caching to avoid searching the entire tree for each test
    # TODO: Requires that the test function name be unique. Add in filename too?
    # TODO: Incorporate new array behavior
    test_name = nodeid.split("::")[-1]
    for path in document.iterdir():
        if test_name in path.read_text():
            # TODO: Is reading from yaml more appropriate?
            return path
    raise RuntimeWarning(f"Could not locate a Doorstop item for {nodeid}")


def record_outcome(doorstop_item: pathlib.Path, outcome: str, commit_hash: str, xfail: bool) -> None:
    """Write the outcome to the doorstop item."""
    # TODO: Use the doorstop API to write this --> item.set(key, value)
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


def pytest_report_teststatus(report, config) -> None:
    """Collect test status and record in the doorstop item if appropriate."""
    document = get_document(config)
    if document:
        if report.when == "call":
            try:
                doorstop_item = get_doorstop_item(report.nodeid, document)
                xfail = "xfail" in report.keywords
                commit_hash = get_commit_hash()  # TODO: Only call this once per session
                record_outcome(doorstop_item, report.outcome, commit_hash, xfail)
            except RuntimeWarning:
                # TODO: Print the warning if a verbose flag is passed
                pass
