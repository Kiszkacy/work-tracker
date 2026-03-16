import pytest

from work_tracker.command.commands.workday import WorkdayHandler


@pytest.mark.order(1)
def test_init(workday_handler: WorkdayHandler):
    assert workday_handler is not None
