from typing import Any

import pytest

from tests.conftest import handle_call, TestInputOutput
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.command_history import CommandHistoryEntry
from work_tracker.command.commands.undo import UndoHandler
from work_tracker.common import Date


@pytest.mark.order(1)
def test_init(undo_handler: UndoHandler):
    assert undo_handler is not None


def test_should_undo_one_step_by_default(undo_handler: UndoHandler, random_date: Date):
    states: list[CommandHistoryEntry] = [
        CommandHistoryEntry(state_key="key0", command="remote"),
        CommandHistoryEntry(state_key="key1", command="office"),
    ]

    result: CommandHandlerResult = handle_call(undo_handler, active_date=random_date, states=states, current_state_index=1)

    assert result.change_state_by == -1
    assert result.error is None


def test_should_undo_multiple_steps_with_count_argument(undo_handler: UndoHandler, random_date: Date):
    states: list[CommandHistoryEntry] = [
        CommandHistoryEntry(state_key="key0", command="remote"),
        CommandHistoryEntry(state_key="key1", command="office"),
        CommandHistoryEntry(state_key="key2", command="done"),
    ]

    result: CommandHandlerResult = handle_call(undo_handler, active_date=random_date, states=states, current_state_index=2, arguments=[2])

    assert result.change_state_by == -2
    assert result.error is None


def test_should_clamp_undo_steps_to_available_history(undo_handler: UndoHandler, random_date: Date):
    states: list[CommandHistoryEntry] = [
        CommandHistoryEntry(state_key="key0", command="remote"),
        CommandHistoryEntry(state_key="key1", command="office"),
    ]

    result: CommandHandlerResult = handle_call(undo_handler, active_date=random_date, states=states, current_state_index=1, arguments=[10])

    assert result.change_state_by == -1
    assert result.error is None


def test_should_output_message_when_already_at_first_state(undo_handler: UndoHandler, random_date: Date):
    states: list[CommandHistoryEntry] = [
        CommandHistoryEntry(state_key="key0", command="remote"),
        CommandHistoryEntry(state_key="key1", command="office"),
    ]

    result: CommandHandlerResult = handle_call(undo_handler, active_date=random_date, states=states, current_state_index=0)

    assert TestInputOutput.get_output() is not None
    assert result.change_state_by is None
    assert result.error is None


def test_should_output_message_when_history_is_empty(undo_handler: UndoHandler, random_date: Date):
    result: CommandHandlerResult = handle_call(undo_handler, active_date=random_date, states=[], current_state_index=0)

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_return_error_on_zero_count(undo_handler: UndoHandler):
    result: CommandHandlerResult = handle_call(undo_handler, arguments=[0])

    assert result.error is not None


def test_should_return_error_on_negative_count(undo_handler: UndoHandler):
    result: CommandHandlerResult = handle_call(undo_handler, arguments=[-1])

    assert result.error is not None


def test_should_return_error_on_too_many_arguments(undo_handler: UndoHandler):
    arguments: list[Any] = [1, 2]

    result: CommandHandlerResult = handle_call(undo_handler, arguments=arguments)

    assert result.error is not None


def test_should_return_error_on_invalid_date_count(undo_handler: UndoHandler, random_date: Date):
    result: CommandHandlerResult = handle_call(undo_handler, dates=[random_date.to_day_date()])

    assert result.error is not None
