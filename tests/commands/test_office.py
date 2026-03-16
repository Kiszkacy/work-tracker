import pytest

from work_tracker.command.commands.office import OfficeHandler


@pytest.mark.order(1)
def test_init(office_handler: OfficeHandler):
    assert office_handler is not None
