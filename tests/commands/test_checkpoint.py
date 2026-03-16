import pytest

from work_tracker.command.commands.checkpoint import CheckpointHandler


@pytest.mark.order(1)
def test_init(checkpoint_handler: CheckpointHandler):
    assert checkpoint_handler is not None
