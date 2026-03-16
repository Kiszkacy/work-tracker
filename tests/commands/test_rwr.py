import pytest

from work_tracker.command.commands.rwr import RwrHandler


@pytest.mark.order(1)
def test_init(rwr_handler: RwrHandler):
    assert rwr_handler is not None
