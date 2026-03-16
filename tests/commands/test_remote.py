import pytest

from work_tracker.command.commands.remote import RemoteHandler


@pytest.mark.order(1)
def test_init(remote_handler: RemoteHandler):
    assert remote_handler is not None
