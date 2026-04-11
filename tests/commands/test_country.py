import datetime

import pytest
from workalendar.registry import registry

from tests.conftest import handle_call, TestInputOutput
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.country import CountryHandler
from work_tracker.common import AppData, Date, DayType


@pytest.mark.order(1)
def test_init(country_handler: CountryHandler):
    assert country_handler is not None


def test_should_display_current_country_code(country_handler: CountryHandler):
    result: CommandHandlerResult = handle_call(country_handler)

    assert result.error is None
    assert result.undoable is False
    assert country_handler.data.country_code in TestInputOutput.get_output().strip()


def test_should_change_country_code(country_handler: CountryHandler, mocker):
    mocker.patch("work_tracker.command.commands.country.CheckpointManager.save")
    original_code: str = country_handler.data.country_code

    result: CommandHandlerResult = handle_call(country_handler, arguments=["DK"])

    assert result.error is None
    assert result.undoable is True
    assert country_handler.data.country_code == "DK"
    assert country_handler.data.country_code != original_code


def test_should_save_checkpoint_on_change(country_handler: CountryHandler, mocker):
    save_mock = mocker.patch("work_tracker.command.commands.country.CheckpointManager.save")

    handle_call(country_handler, arguments=["DK"])

    save_mock.assert_called_once()


def test_should_return_error_on_invalid_country_code(country_handler: CountryHandler):
    original_code: str = country_handler.data.country_code

    result: CommandHandlerResult = handle_call(country_handler, arguments=["INVALID_CODE"])

    assert result.error is None
    assert result.undoable is False
    assert TestInputOutput.get_output().strip() is not None
    assert country_handler.data.country_code == original_code


def test_should_not_change_when_same_code_provided(country_handler: CountryHandler, mocker):
    save_mock = mocker.patch("work_tracker.command.commands.country.CheckpointManager.save")

    result: CommandHandlerResult = handle_call(country_handler, arguments=["PL"])

    assert result.error is None
    assert result.undoable is False
    save_mock.assert_not_called()


def test_should_accept_lowercase_country_code(country_handler: CountryHandler, mocker):
    mocker.patch("work_tracker.command.commands.country.CheckpointManager.save")

    result: CommandHandlerResult = handle_call(country_handler, arguments=["dk"])

    assert result.error is None
    assert result.undoable is True
    assert country_handler.data.country_code == "DK"


def test_should_return_error_on_too_many_arguments(country_handler: CountryHandler):
    original_code: str = country_handler.data.country_code

    result: CommandHandlerResult = handle_call(country_handler, arguments=["DK", "extra"])

    assert result.error is not None
    assert country_handler.data.country_code == original_code


_NOV_1_2024: Date = Date.from_datetime(datetime.date(2024, 11, 1)) # friday


def test_pl_nov_1_is_holiday(): # sanity check
    pl_calendar = registry.get_calendars()["PL"]()
    dk_calendar = registry.get_calendars()["DK"]()
    assert pl_calendar.is_holiday(_NOV_1_2024.to_datetime())
    assert dk_calendar.is_working_day(_NOV_1_2024.to_datetime())


def test_holiday_changed_to_workday_when_switching_from_pl_to_dk():
    data: AppData = AppData(country_code="PL")
    _ = data.day[_NOV_1_2024]
    assert data.day[_NOV_1_2024].day_type == DayType.HOLIDAY

    data.change_country_code("DK")

    assert data.country_code == "DK"
    assert data.day[_NOV_1_2024].day_type == DayType.WORKDAY


def test_manually_set_day_not_changed_when_switching_from_pl_to_dk():
    data: AppData = AppData(country_code="PL")
    _ = data.day[_NOV_1_2024]
    assert data.day[_NOV_1_2024].day_type == DayType.HOLIDAY

    data.day[_NOV_1_2024].day_type = DayType.WEEKEND
    data.change_country_code("DK")

    assert data.day[_NOV_1_2024].day_type == DayType.WEEKEND


def test_workday_changed_to_holiday_when_switching_from_dk_to_pl():
    data: AppData = AppData(country_code="DK")
    _ = data.day[_NOV_1_2024]
    assert data.day[_NOV_1_2024].day_type == DayType.WORKDAY

    data.change_country_code("PL")

    assert data.day[_NOV_1_2024].day_type == DayType.HOLIDAY


def test_manually_set_day_not_changed_when_switching_from_dk_to_pl():
    data: AppData = AppData(country_code="DK")
    _ = data.day[_NOV_1_2024]
    assert data.day[_NOV_1_2024].day_type == DayType.WORKDAY

    data.day[_NOV_1_2024].day_type = DayType.WEEKEND
    data.change_country_code("PL")

    assert data.day[_NOV_1_2024].day_type == DayType.WEEKEND


def test_uninitialized_days_use_new_calendar_after_switch():
    data: AppData = AppData(country_code="DK")

    data.change_country_code("PL")

    assert data.day[_NOV_1_2024].day_type == DayType.HOLIDAY
