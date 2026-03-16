import pytest

from work_tracker.command.commands.history import HistoryHandler


@pytest.mark.order(1)
def test_init(history_handler: HistoryHandler):
    assert history_handler is not None
