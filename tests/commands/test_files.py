from typing import Any

import pytest

from tests.conftest import TestInputOutput, handle_call
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.files import FilesHandler
from work_tracker.common import get_data_path


@pytest.mark.order(1)
def test_init(files_handler: FilesHandler):
    assert files_handler is not None


def test_should_output_data_directory_path(files_handler: FilesHandler):
    result: CommandHandlerResult = handle_call(files_handler)

    assert TestInputOutput.get_output().strip() == str(get_data_path())
    assert result.error is None


def test_should_return_error_on_invalid_argument_count(files_handler: FilesHandler):
    arguments: list[Any] = ["value"]

    result: CommandHandlerResult = handle_call(files_handler, arguments=arguments)

    assert result.error is not None
