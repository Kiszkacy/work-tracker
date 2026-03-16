import pytest

from work_tracker.command.commands.undo import UndoHandler


@pytest.mark.order(1)
def test_init(undo_handler: UndoHandler):
    assert undo_handler is not None
