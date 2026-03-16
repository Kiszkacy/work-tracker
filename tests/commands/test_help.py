import pytest

from work_tracker.command.commands.help import HelpHandler


@pytest.mark.order(1)
def test_init(help_handler: HelpHandler):
    assert help_handler is not None
