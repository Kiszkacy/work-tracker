import pytest

from work_tracker.command.commands.deletemacro import DeletemacroHandler


@pytest.mark.order(1)
def test_init(deletemacro_handler: DeletemacroHandler):
    assert deletemacro_handler is not None
