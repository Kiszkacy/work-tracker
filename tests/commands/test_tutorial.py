from typing import Any

import pytest

from tests.conftest import handle_call, TestInputOutput
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.tutorial import TutorialHandler
from work_tracker.common import Date


@pytest.mark.order(1)
def test_init(tutorial_handler: TutorialHandler):
    assert tutorial_handler is not None


def test_should_display_first_page_as_argument(tutorial_handler: TutorialHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(tutorial_handler, active_date=date, arguments=[1])

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_display_second_page_as_argument(tutorial_handler: TutorialHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(tutorial_handler, active_date=date, arguments=[2])

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_return_error_on_zero_page_argument(tutorial_handler: TutorialHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(tutorial_handler, active_date=date, arguments=[0])

    assert result.error is not None


def test_should_return_error_on_page_out_of_range(tutorial_handler: TutorialHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    out_of_range_page: int = len(tutorial_handler.pages) + 1

    result: CommandHandlerResult = handle_call(tutorial_handler, active_date=date, arguments=[out_of_range_page])

    assert result.error is not None


def test_should_return_error_on_too_many_arguments(tutorial_handler: TutorialHandler):
    arguments: list[Any] = [1, 2]

    result: CommandHandlerResult = handle_call(tutorial_handler, arguments=arguments)

    assert result.error is not None


def test_should_return_error_on_invalid_date_count(tutorial_handler: TutorialHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(tutorial_handler, dates=[date])

    assert result.error is not None
