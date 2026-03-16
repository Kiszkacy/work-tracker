import pytest

from work_tracker.command.commands.dayoff import DayoffHandler


@pytest.mark.order(1)
def test_init(dayoff_handler: DayoffHandler):
    assert dayoff_handler is not None
