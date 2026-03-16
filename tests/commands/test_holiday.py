import pytest

from work_tracker.command.commands.holiday import HolidayHandler


@pytest.mark.order(1)
def test_init(holiday_handler: HolidayHandler):
    assert holiday_handler is not None
