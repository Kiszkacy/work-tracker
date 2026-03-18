from typing import Any

import pytest

from tests.conftest import handle_call, TestInputOutput
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.command_history import CommandHistoryEntry
from work_tracker.command.commands.history import HistoryHandler
from work_tracker.common import Date


@pytest.mark.order(1)
def test_init(history_handler: HistoryHandler):
    assert history_handler is not None


def test_should_output_state_history(history_handler: HistoryHandler, random_date: Date):
    states: list[CommandHistoryEntry] = [
        CommandHistoryEntry(state_key="key0", command="remote"),
        CommandHistoryEntry(state_key="key1", command="office"),
        CommandHistoryEntry(state_key="key2", command="done"),
    ]

    result: CommandHandlerResult = handle_call(history_handler, active_date=random_date, states=states, current_state_index=2)

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_output_history_containing_command_names(history_handler: HistoryHandler, random_date: Date):
    states: list[CommandHistoryEntry] = [
        CommandHistoryEntry(state_key="key0", command="remote"),
        CommandHistoryEntry(state_key="key1", command="office"),
    ]

    result: CommandHandlerResult = handle_call(history_handler, active_date=random_date, states=states, current_state_index=1)

    output: str = TestInputOutput.get_output()
    assert output is not None
    assert "remote" in output
    assert "office" in output
    assert result.error is None


def test_should_output_history_with_single_state(history_handler: HistoryHandler, random_date: Date):
    states: list[CommandHistoryEntry] = [
        CommandHistoryEntry(state_key="key0", command="done"),
    ]

    result: CommandHandlerResult = handle_call(history_handler, active_date=random_date, states=states, current_state_index=0)

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_return_error_on_invalid_argument_count(history_handler: HistoryHandler):
    arguments: list[Any] = ["value"]

    result: CommandHandlerResult = handle_call(history_handler, arguments=arguments)

    assert result.error is not None


def test_should_return_error_on_invalid_date_count(history_handler: HistoryHandler, random_date: Date):
    result: CommandHandlerResult = handle_call(history_handler, dates=[random_date.to_day_date()])

    assert result.error is not None
