import pytest

from work_tracker.command.commands.tutorial import TutorialHandler


@pytest.mark.order(1)
def test_init(tutorial_handler: TutorialHandler):
    assert tutorial_handler is not None
