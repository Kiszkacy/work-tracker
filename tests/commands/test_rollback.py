import pytest
from pytest_mock import MockerFixture

from tests.conftest import handle_call, TestInputOutput, sample_data
from work_tracker.checkpoint_manager import CheckpointManager, CheckpointTemplate
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.rollback import RollbackHandler
from work_tracker.common import Date, AppData
from path import Path


@pytest.fixture()
def fake_checkpoint() -> CheckpointTemplate:
    return CheckpointTemplate(
        path=Path("."),
        full_identifier="user.test-checkpoint__2026-03-18_11-00-00",
        name="user.test-checkpoint",
        date="2026-03-18_11-00-00",
        persistent=True,
    )


@pytest.mark.order(1)
def test_init(rollback_handler: RollbackHandler):
    assert rollback_handler is not None


def test_should_load_data_from_checkpoint(
    rollback_handler: RollbackHandler,
    mocker: MockerFixture,
    random_date: Date,
    fake_checkpoint: CheckpointTemplate,
):
    date: Date = random_date.to_day_date()
    source_data: AppData = sample_data()
    source_data.day[date].minutes_at_work = 999
    mocker.patch.object(CheckpointManager, "checkpoints", return_value=[fake_checkpoint])
    mocker.patch("os.path.getctime", return_value=0.0)
    mocker.patch.object(CheckpointManager, "load", return_value=source_data)
    rollback_handler.data.day[date].minutes_at_work = 0

    result: CommandHandlerResult = handle_call(rollback_handler, active_date=date, arguments=["test-checkpoint"])

    assert rollback_handler.data.day[date].minutes_at_work == 999
    assert result.error is None


def test_should_output_message_when_checkpoint_not_found(
    rollback_handler: RollbackHandler,
    mocker: MockerFixture,
    random_date: Date,
):
    date: Date = random_date.to_day_date()
    mocker.patch.object(CheckpointManager, "checkpoints", return_value=[])

    result: CommandHandlerResult = handle_call(rollback_handler, active_date=date, arguments=["nosuchcheckpoint"])

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_return_error_on_no_arguments(rollback_handler: RollbackHandler):
    result: CommandHandlerResult = handle_call(rollback_handler)

    assert result.error is not None


def test_should_return_error_on_too_many_arguments(rollback_handler: RollbackHandler):
    result: CommandHandlerResult = handle_call(rollback_handler, arguments=["value", "extra"])

    assert result.error is not None


def test_should_return_error_on_invalid_date_count(rollback_handler: RollbackHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(rollback_handler, dates=[date])

    assert result.error is not None
