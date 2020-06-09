"""Plug to record test results in a Doorstop document."""
import pathlib
import itertools

import doorstop
import git


def pytest_addoption(parser):
    """Add parser argument for doorstop document."""
    group = parser.getgroup("doorstop", "mark doorstop items with test results")
    group._addoption(
        "--doorstop_prefix",
        action="store",
        dest="doorstop_prefix",
        type=str,
        help="Prefix for the test items",
    )

    group._addoption(
        "--doorstop_path",
        action="store",
        dest="doorstop_path",
        type=str,
        default=str(pathlib.Path.cwd()),
        help="Location of the doorstop test items",
    )


def pytest_configure(config):
    """Register the plugin."""
    if not (
        config.option.doorstop_prefix
        or (config.option.doorstop_path != str(pathlib.Path.cwd()))
    ):
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
        self.tree = doorstop.build(root=config.option.doorstop_path)

        # Check that there is at least one document in the tree
        if not self.tree.documents:
            # Try to build a tree using each first-level child of the path
            children = list(pathlib.Path(config.option.doorstop_path).glob("*"))
            while children:
                path = children.pop()
                self.tree = doorstop.build(root=path)
                if self.tree.documents:
                    break
            else:
                raise RuntimeError(
                    f"Could not find a Doorstop document in the path "
                    f"{config.option.doorstop_path} or its children."
                )

    def pytest_sessionstart(self, session) -> None:
        """Perform setup activities at start of session."""
        self.commit_hash = self.get_commit_hash()
        self.document = self.get_document()

    def get_commit_hash(self) -> str:
        """Return the full git hash for the current commit."""
        repo = git.Repo(search_parent_directories=True)
        return repo.head.object.hexsha

    def get_document(self) -> doorstop.Document:
        """Convert commandline argument to a document object."""
        # Find the Doorstop document with user-specified prefix
        if self.config.option.doorstop_prefix:
            doorstop_document = self.tree.find_document(
                self.config.option.doorstop_prefix
            )
        else:
            # Try to find a Doorstop document with user-specified path
            provided_path = pathlib.Path(self.config.option.doorstop_path).resolve()
            for doc in self.tree.documents:
                doc_path = pathlib.Path(doc.path).resolve()
                if provided_path == doc_path:
                    doorstop_document = doc
                    break
        return doorstop_document

    def get_doorstop_item(self, nodeid: str) -> doorstop.Item:
        """Search for the doorstop item that contains the test."""
        test_name = nodeid.split("::")[-1]
        for item in self.document.items:
            if type(item.references) is list:
                refs = "`".join(
                    itertools.chain.from_iterable(
                        [ref.values() for ref in item.references]
                    )
                )
            else:
                refs = str(item.ref)
            if test_name in refs:
                return item
        raise RuntimeWarning(f"Could not locate a Doorstop item for {nodeid}")

    def record_outcome(
        self, doorstop_item: doorstop.Item, outcome: str, xfail: bool
    ) -> None:
        """Write the outcome to the doorstop item."""
        doorstop_item.set("test_commit_latest", self.commit_hash)
        if not xfail:
            doorstop_item.set("test_result_latest", outcome)
            if outcome == "passed":
                doorstop_item.set("test_commit_last_passed", self.commit_hash)
        else:
            if outcome == "skipped":
                doorstop_item.set("test_result_latest", "xfail")
            elif outcome == "passed":
                doorstop_item.set("test_result_latest", "xpass")
        if self.config.option.verbose:
            print(
                f"""\nWriting outcome ({doorstop_item.get("test_result_latest")})"""
                f""" for doorstop item {str(doorstop_item.uid)}"""
            )

    def pytest_runtest_logreport(self, report) -> None:
        """Collect test status and record in the doorstop item if appropriate."""
        if self.document and report.when == "call":
            try:
                doorstop_item = self.get_doorstop_item(report.nodeid)
                xfail = "xfail" in report.keywords
                self.record_outcome(doorstop_item, report.outcome, xfail)
            except RuntimeWarning as e:
                if self.config.option.verbose:
                    print("\n")
                    print(e)
