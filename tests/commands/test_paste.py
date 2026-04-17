import pytest

pytestmark = pytest.mark.order(after="tests/commands/test_copy.py")

from tests.conftest import handle_call
from work_tracker.command.clipboard import Clipboard
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.paste import PasteHandler
from work_tracker.common import Date, DayData, Mode, WorkLocation, Time, AttendanceType, DayType


def _populate_clipboard(**kwargs) -> DayData:
    data: DayData = DayData()
    for key, value in kwargs.items():
        setattr(data, key, value)
    Clipboard.set(Clipboard.COPY_PASTE_KEY, data)
    return data


@pytest.mark.order(1)
def test_init(paste_handler: PasteHandler):
    assert paste_handler is not None


def test_should_paste_to_active_day(paste_handler: PasteHandler, random_date: Date):
    target_date: Date = random_date.to_day_date()
    _populate_clipboard(minutes_at_work=360, work_location=WorkLocation.REMOTE)

    result: CommandHandlerResult = handle_call(paste_handler, active_date=target_date)

    assert result.error is None
    assert paste_handler.data.day[target_date].minutes_at_work == 360
    assert paste_handler.data.day[target_date].work_location == WorkLocation.REMOTE


def test_should_paste_to_multiple_explicit_dates(paste_handler: PasteHandler, random_dates: list[Date]):
    _populate_clipboard(minutes_at_work=240)

    target_dates: list[Date] = [date.to_day_date() for date in random_dates]
    result: CommandHandlerResult = handle_call(paste_handler, dates=target_dates)

    assert result.error is None
    for date in target_dates:
        assert paste_handler.data.day[date].minutes_at_work == 240


def test_should_paste_all_fields(paste_handler: PasteHandler, random_date: Date):
    source: DayData = _populate_clipboard(
        attendance_type=AttendanceType.PRESENT,
        day_type=DayType.WORKDAY,
        work_location=WorkLocation.REMOTE,
        minutes_at_work=111,
        target_minutes=222,
        work_start=Time(minutes_since_midnight=7 * 60),
        work_end=Time(minutes_since_midnight=14 * 60 + 51),
    )

    target_date: Date = random_date.to_day_date()
    handle_call(paste_handler, active_date=target_date)

    target_data: DayData = paste_handler.data.day[target_date]
    assert target_data.attendance_type == source.attendance_type
    assert target_data.day_type == source.day_type
    assert target_data.work_location == source.work_location
    assert target_data.minutes_at_work == source.minutes_at_work
    assert target_data.target_minutes == source.target_minutes
    assert target_data.work_start.minutes_since_midnight == source.work_start.minutes_since_midnight
    assert target_data.work_end.minutes_since_midnight == source.work_end.minutes_since_midnight


def test_should_return_error_when_clipboard_is_empty(paste_handler: PasteHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(paste_handler, active_date=date)

    assert result.error is not None


def test_should_return_error_when_mode_is_month_and_no_date_given(paste_handler: PasteHandler, random_date: Date):
    _populate_clipboard()

    month: Date = random_date.to_month_date()
    result: CommandHandlerResult = handle_call(paste_handler, active_date=month, mode=Mode.Month)

    assert result.error is not None


def test_should_return_error_when_a_month_date_is_in_dates(paste_handler: PasteHandler, random_date: Date):
    _populate_clipboard()

    month: Date = random_date.to_month_date()
    result: CommandHandlerResult = handle_call(paste_handler, dates=[month])

    assert result.error is not None


def test_should_return_error_on_invalid_argument_count(paste_handler: PasteHandler, random_date: Date):
    _populate_clipboard()

    result: CommandHandlerResult = handle_call(paste_handler, arguments=["value"])

    assert result.error is not None
