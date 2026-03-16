import pytest

from work_tracker.command.commands.end import EndHandler


@pytest.mark.order(1)
def test_init(end_handler: EndHandler):
    assert end_handler is not None
