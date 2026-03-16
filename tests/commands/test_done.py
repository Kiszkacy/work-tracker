import pytest

from work_tracker.command.commands.done import DoneHandler


@pytest.mark.order(1)
def test_init(done_handler: DoneHandler):
    assert done_handler is not None
