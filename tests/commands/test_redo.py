import pytest

from work_tracker.command.commands.redo import RedoHandler


@pytest.mark.order(1)
def test_init(redo_handler: RedoHandler):
    assert redo_handler is not None
