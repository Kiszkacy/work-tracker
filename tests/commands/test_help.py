from typing import Any

import pytest

from tests.conftest import handle_call, TestInputOutput
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.help import HelpHandler
from work_tracker.common import Date


@pytest.mark.order(1)
def test_init(help_handler: HelpHandler):
    assert help_handler is not None


def test_should_output_command_list_when_no_arguments_given(help_handler: HelpHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(help_handler, active_date=date)

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_output_help_for_specific_command(help_handler: HelpHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(help_handler, active_date=date, arguments=["status"])

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_return_error_for_unknown_command_name(help_handler: HelpHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(help_handler, active_date=date, arguments=["nonexistentcommand"])

    assert result.error is not None


def test_should_return_error_on_too_many_arguments(help_handler: HelpHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    arguments: list[Any] = ["status", "extra"]

    result: CommandHandlerResult = handle_call(help_handler, active_date=date, arguments=arguments)

    assert result.error is not None


def test_should_return_error_on_invalid_date_count(help_handler: HelpHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(help_handler, dates=[date])

    assert result.error is not None
