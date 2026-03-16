import pytest

from work_tracker.command.commands.target import TargetHandler


@pytest.mark.order(1)
def test_init(target_handler: TargetHandler):
    assert target_handler is not None
