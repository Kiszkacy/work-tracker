import pytest

from work_tracker.command.commands.alias import AliasHandler


@pytest.mark.order(1)
def test_init(alias_handler: AliasHandler):
    assert alias_handler is not None
