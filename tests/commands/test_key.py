import pytest

from work_tracker.command.commands.key import KeyHandler


@pytest.mark.order(1)
def test_init(key_handler: KeyHandler):
    assert key_handler is not None
