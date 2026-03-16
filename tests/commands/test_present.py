import pytest

from work_tracker.command.commands.present import PresentHandler


@pytest.mark.order(1)
def test_init(present_handler: PresentHandler):
    assert present_handler is not None
