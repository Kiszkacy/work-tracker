import pytest

from work_tracker.command.commands.deletealias import DeletealiasHandler


@pytest.mark.order(1)
def test_init(deletealias_handler: DeletealiasHandler):
    assert deletealias_handler is not None
