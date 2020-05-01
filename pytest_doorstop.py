"""Plug to record test results in a Doorstop document."""
import pathlib

import doorstop
import git
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


def pytest_configure(config):
    """Register the plugin."""
    if not config.option.doorstop_document:
        return
    else:
        Plugin = DoorstopRecorder
    plugin = Plugin(config)
    config.doorstop = plugin
    config.pluginmanager.register(plugin)


def pytest_unconfigure(config):
    """Unregister the plugin."""
    plugin = getattr(config, "doorstop", None)
    if plugin is not None:
        del config.doorstop
        config.pluginmanager.unregister(plugin)


class DoorstopRecorder:
    """Record test results in a Doorstop document."""

    def __init__(self, config):
        """Set config and tree."""
        self.config = config
        self.tree = doorstop.build()

    def pytest_sessionstart(self, session) -> None:
        """Perform setup activities at start of session."""
        self.commit_hash = self.get_commit_hash()
        self.document = self.get_document()

    def get_commit_hash(self) -> str:
        """Return the full git hash for the current commit."""
        repo = git.Repo(search_parent_directories=True)
        return repo.head.object.hexsha

    def get_document(self) -> pathlib.Path:
        """Convert commandline argument to a pathlib object."""
        option = self.config.getoption("doorstop_document")
        try:
            # Find the Doorstop document with user-specified prefix
            doc = self.tree.find_document(option)
            doorstop_document = pathlib.Path(doc.path)
        except doorstop.common.DoorstopError:
            # Try to find a Doorstop document with user-specified path
            docs = self.tree.documents
            path = pathlib.Path(option).resolve()
            paths = [pathlib.Path(doc.path) for doc in docs]
            if path in paths:
                doorstop_document = path
            else:
                raise RuntimeError(
                    f"Could not locate a Doorstop document with prefix or path: {option}"
                )
        return doorstop_document

    def get_doorstop_item(self, nodeid: str) -> pathlib.Path:
        """Search for the doorstop item that contains the test."""
        # TODO: Use the doorstop API to find this --> document.items
        # TODO: Implement caching to avoid searching the entire tree for each test
        # TODO: Requires that the test function name be unique. Add in filename too?
        # TODO: Incorporate new array behavior
        test_name = nodeid.split("::")[-1]
        for path in self.document.iterdir():
            if test_name in path.read_text():
                # TODO: Is reading from yaml more appropriate?
                return path
        raise RuntimeWarning(f"Could not locate a Doorstop item for {nodeid}")

    def record_outcome(
        self, doorstop_item: pathlib.Path, outcome: str, xfail: bool
    ) -> None:
        """Write the outcome to the doorstop item."""
        # TODO: Use the doorstop API to write this --> item.set(key, value)
        with doorstop_item.open("r") as f:
            contents = yaml.safe_load(f)
        contents["test_commit_latest"] = self.commit_hash
        if not xfail:
            contents["test_result_latest"] = outcome
            if outcome == "passed":
                contents["test_commit_last_passed"] = self.commit_hash
        else:
            if outcome == "skipped":
                contents["test_result_latest"] = "xfail"
            elif outcome == "passed":
                contents["test_result_latest"] = "xpass"
        with doorstop_item.open("w") as f:
            yaml.safe_dump(contents, f)

    def pytest_report_teststatus(self, report, config) -> None:
        """Collect test status and record in the doorstop item if appropriate."""
        if self.document:
            if report.when == "call":
                try:
                    doorstop_item = self.get_doorstop_item(report.nodeid)
                    xfail = "xfail" in report.keywords
                    self.record_outcome(doorstop_item, report.outcome, xfail)
                except RuntimeWarning as e:
                    # TODO: Print the warning if a verbose flag is passed
                    pass
