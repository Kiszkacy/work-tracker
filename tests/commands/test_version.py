import pytest

from tests.conftest import TestInputOutput, handle_call
from work_tracker import __version__
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.version import VersionHandler


@pytest.mark.order(1)
def test_init(version_handler: VersionHandler):
    assert version_handler is not None


def test_should_output_correct_version_number(version_handler: VersionHandler):
    result: CommandHandlerResult = handle_call(version_handler)

    assert TestInputOutput.get_output().strip() == __version__
    assert result.error is None


def test_should_return_error_on_invalid_argument_count(version_handler: VersionHandler):
    arguments: list[any] = ["value"]

    result: CommandHandlerResult = handle_call(version_handler, arguments=arguments)

    assert result.error is not None