import pytest

from work_tracker.command.commands.macro import MacroHandler


@pytest.mark.order(1)
def test_init(macro_handler: MacroHandler):
    assert macro_handler is not None
