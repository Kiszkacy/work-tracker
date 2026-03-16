import pytest

from work_tracker.command.commands.config import ConfigHandler


@pytest.mark.order(1)
def test_init(config_handler: ConfigHandler):
    assert config_handler is not None
