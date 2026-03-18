from typing import Any

import pytest

from tests.conftest import handle_call, TestInputOutput
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.command_history import CommandHistoryEntry
from work_tracker.command.commands.redo import RedoHandler
from work_tracker.common import Date


@pytest.mark.order(1)
def test_init(redo_handler: RedoHandler):
    assert redo_handler is not None


def test_should_redo_one_step_by_default(redo_handler: RedoHandler, random_date: Date):
    states: list[CommandHistoryEntry] = [
        CommandHistoryEntry(state_key="key0", command="remote"),
        CommandHistoryEntry(state_key="key1", command="office"),
    ]

    result: CommandHandlerResult = handle_call(redo_handler, active_date=random_date, states=states, current_state_index=0)

    assert result.change_state_by == 1
    assert result.error is None


def test_should_redo_multiple_steps_with_count_argument(redo_handler: RedoHandler, random_date: Date):
    states: list[CommandHistoryEntry] = [
        CommandHistoryEntry(state_key="key0", command="remote"),
        CommandHistoryEntry(state_key="key1", command="office"),
        CommandHistoryEntry(state_key="key2", command="done"),
    ]

    result: CommandHandlerResult = handle_call(redo_handler, active_date=random_date, states=states, current_state_index=0, arguments=[2])

    assert result.change_state_by == 2
    assert result.error is None


def test_should_clamp_redo_steps_to_available_history(redo_handler: RedoHandler, random_date: Date):
    states: list[CommandHistoryEntry] = [
        CommandHistoryEntry(state_key="key0", command="remote"),
        CommandHistoryEntry(state_key="key1", command="office"),
    ]

    result: CommandHandlerResult = handle_call(redo_handler, active_date=random_date, states=states, current_state_index=0, arguments=[10])

    assert result.change_state_by == 1
    assert result.error is None


def test_should_output_message_when_already_at_last_state(redo_handler: RedoHandler, random_date: Date):
    states: list[CommandHistoryEntry] = [
        CommandHistoryEntry(state_key="key0", command="remote"),
        CommandHistoryEntry(state_key="key1", command="office"),
    ]

    result: CommandHandlerResult = handle_call(redo_handler, active_date=random_date, states=states, current_state_index=1)

    assert TestInputOutput.get_output() is not None
    assert result.change_state_by is None
    assert result.error is None


def test_should_output_message_when_history_is_empty(redo_handler: RedoHandler, random_date: Date):
    result: CommandHandlerResult = handle_call(redo_handler, active_date=random_date, states=[], current_state_index=0)

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_return_error_on_zero_count(redo_handler: RedoHandler):
    result: CommandHandlerResult = handle_call(redo_handler, arguments=[0])

    assert result.error is not None


def test_should_return_error_on_negative_count(redo_handler: RedoHandler):
    result: CommandHandlerResult = handle_call(redo_handler, arguments=[-1])

    assert result.error is not None


def test_should_return_error_on_too_many_arguments(redo_handler: RedoHandler):
    arguments: list[Any] = [1, 2]

    result: CommandHandlerResult = handle_call(redo_handler, arguments=arguments)

    assert result.error is not None


def test_should_return_error_on_invalid_date_count(redo_handler: RedoHandler, random_date: Date):
    result: CommandHandlerResult = handle_call(redo_handler, dates=[random_date.to_day_date()])

    assert result.error is not None
