import pytest

from work_tracker.command.commands.version import VersionHandler


@pytest.mark.order(1)
def test_init(version_handler: VersionHandler):
    assert version_handler is not None
