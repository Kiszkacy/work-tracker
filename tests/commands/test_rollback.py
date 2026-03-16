import pytest

from work_tracker.command.commands.rollback import RollbackHandler


@pytest.mark.order(1)
def test_init(rollback_handler: RollbackHandler):
    assert rollback_handler is not None
