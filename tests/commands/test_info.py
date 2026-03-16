import pytest

from work_tracker.command.commands.info import InfoHandler


@pytest.mark.order(1)
def test_init(info_handler: InfoHandler):
    assert info_handler is not None
