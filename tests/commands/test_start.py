import pytest

from work_tracker.command.commands.start import StartHandler


@pytest.mark.order(1)
def test_init(start_handler: StartHandler):
    assert start_handler is not None
