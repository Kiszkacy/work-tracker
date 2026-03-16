import pytest

from work_tracker.command.commands.status import StatusHandler


@pytest.mark.order(1)
def test_init(status_handler: StatusHandler):
    assert status_handler is not None
