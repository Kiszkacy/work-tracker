import pytest

from work_tracker.command.commands.absence import AbsenceHandler


@pytest.mark.order(1)
def test_init(absence_handler: AbsenceHandler):
    assert absence_handler is not None
