import pytest

from work_tracker.command.commands.keyword import KeywordHandler


@pytest.mark.order(1)
def test_init(keyword_handler: KeywordHandler):
    assert keyword_handler is not None
