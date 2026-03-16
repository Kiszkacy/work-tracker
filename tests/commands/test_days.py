import pytest

from work_tracker.command.commands.days import DaysHandler


@pytest.mark.order(1)
def test_init(days_handler: DaysHandler):
    assert days_handler is not None
