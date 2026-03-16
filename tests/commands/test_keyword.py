import pytest

from tests.conftest import TestInputOutput, handle_call
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.keyword import KeywordHandler


@pytest.mark.order(1)
def test_init(keyword_handler: KeywordHandler):
    assert keyword_handler is not None


def test_should_output_keyword_list(keyword_handler: KeywordHandler):
    result: CommandHandlerResult = handle_call(keyword_handler)

    assert TestInputOutput.get_output().strip() is not None
    assert result.error is None


def test_should_return_error_on_invalid_argument_count(keyword_handler: KeywordHandler):
    arguments: list[any] = ["value"]

    result: CommandHandlerResult = handle_call(keyword_handler, arguments=arguments)

    assert result.error is not None