import pytest

from work_tracker.command.commands.minutes import MinutesHandler


@pytest.mark.order(1)
def test_init(minutes_handler: MinutesHandler):
    assert minutes_handler is not None
