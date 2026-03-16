import pytest

from work_tracker.command.commands.zero import ZeroHandler


@pytest.mark.order(1)
def test_init(zero_handler: ZeroHandler):
    assert zero_handler is not None
