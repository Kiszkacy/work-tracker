from typing import Any

import pytest

from tests.conftest import handle_call, sample_data
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.key import KeyHandler
from work_tracker.command.common import KeyManager
from work_tracker.common import Date


@pytest.mark.order(1)
def test_init(key_handler: KeyHandler):
    assert key_handler is not None


def test_should_import_data_from_encoded_key(key_handler: KeyHandler, random_date: Date):
    source_data = sample_data()
    date: Date = random_date.to_day_date()
    source_data.day[date].minutes_at_work = 300
    encoded_key: str = KeyManager.encode(source_data)

    result: CommandHandlerResult = handle_call(key_handler, arguments=[encoded_key])

    assert key_handler.data.day[date].minutes_at_work == 300
    assert result.error is None


def test_should_return_error_on_invalid_date_count(key_handler: KeyHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(key_handler, dates=[date])

    assert result.error is not None


def test_should_return_error_on_too_many_arguments(key_handler: KeyHandler):
    arguments: list[Any] = ["value", "extra"]

    result: CommandHandlerResult = handle_call(key_handler, arguments=arguments)

    assert result.error is not None
