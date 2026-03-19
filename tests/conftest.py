import datetime
import random
from typing import Any
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from workalendar.registry import registry

from work_tracker import WorkTracker
from work_tracker.command.command_handler import CommandHandler, CommandHandlerResult
from work_tracker.command.command_history import CommandHistoryEntry
from work_tracker.command.commands.absence import AbsenceHandler
from work_tracker.command.commands.alias import AliasHandler
from work_tracker.command.commands.calendar import CalendarHandler
from work_tracker.command.commands.checkpoint import CheckpointHandler
from work_tracker.command.commands.clear import ClearHandler
from work_tracker.command.commands.config import ConfigHandler
from work_tracker.command.commands.dayoff import DayoffHandler
from work_tracker.command.commands.days import DaysHandler
from work_tracker.command.commands.deletealias import DeletealiasHandler
from work_tracker.command.commands.deletemacro import DeletemacroHandler
from work_tracker.command.commands.done import DoneHandler
from work_tracker.command.commands.end import EndHandler
from work_tracker.command.commands.exit import ExitHandler
from work_tracker.command.commands.files import FilesHandler
from work_tracker.command.commands.fte import FteHandler
from work_tracker.command.commands.help import HelpHandler
from work_tracker.command.commands.history import HistoryHandler
from work_tracker.command.commands.holiday import HolidayHandler
from work_tracker.command.commands.info import InfoHandler
from work_tracker.command.commands.key import KeyHandler
from work_tracker.command.commands.keyword import KeywordHandler
from work_tracker.command.commands.macro import MacroHandler
from work_tracker.command.commands.minutes import MinutesHandler
from work_tracker.command.commands.office import OfficeHandler
from work_tracker.command.commands.present import PresentHandler
from work_tracker.command.commands.redo import RedoHandler
from work_tracker.command.commands.remote import RemoteHandler
from work_tracker.command.commands.rollback import RollbackHandler
from work_tracker.command.commands.rwr import RwrHandler
from work_tracker.command.commands.start import StartHandler
from work_tracker.command.commands.status import StatusHandler
from work_tracker.command.commands.target import TargetHandler
from work_tracker.command.commands.tutorial import TutorialHandler
from work_tracker.command.commands.undo import UndoHandler
from work_tracker.command.commands.version import VersionHandler
from work_tracker.command.commands.workday import WorkdayHandler
from work_tracker.command.commands.zero import ZeroHandler
from work_tracker.command.commands import __date as _date_module
from work_tracker.command.commands import __time as _time_module
from work_tracker.command.commands import __macro as _macro_module
from work_tracker.command.common import CommandArgument
from work_tracker.common import AppData, Date, Mode, ReadonlyAppState, classproperty
from work_tracker.text.input_output_handler import InputOutputHandler


_DateHandler = getattr(_date_module, "__DateHandler")
_TimeHandler = getattr(_time_module, "__TimeHandler")
_MacroHandler = getattr(_macro_module, "__MacroHandler")


class TestInputOutput:
    _text: str = ""
    _input_queue: list[str] = [] # TODO change to proper queue structure
    _output_queue: list[str] = []

    @classmethod
    def clear(cls):
        cls._text = ""
        cls._input_queue = []
        cls._output_queue = []

    @classmethod
    def reset_text(cls):
        cls._text = ""

    @classproperty
    def text(cls) -> str:
        return cls._text

    @classmethod
    def write(cls, text: str):
        cls._text += text

    @classmethod
    def output(cls, text: str):
        cls.write(text)
        cls._output_queue.append(cls._text)
        cls.reset_text()

    @classmethod
    def append_input(cls, text: str):
        cls._input_queue.append(text)

    @classmethod
    def get_input(cls) -> str | None:
        if len(cls._input_queue) == 0:
            return None
        return cls._input_queue.pop(0)

    @classmethod
    def get_output(cls) -> str | None:
        if len(cls._output_queue) == 0:
            return None
        return cls._output_queue.pop(0)


def mock_io(mocker: MockerFixture) -> InputOutputHandler:
    io_mock: MagicMock = mocker.patch("work_tracker.text.input_output_handler.InputOutputHandler", autospec=True)

    def mock_output(text: str = "", end: str = "\n", *args, **kwargs):
        TestInputOutput.output(f"{text}{end}")

    def mock_write(text: str = "", end: str = "\n", *args, **kwargs):
        TestInputOutput.write(f"{text}{end}")

    io_mock.output.side_effect = mock_output
    io_mock.write.side_effect = mock_write

    return io_mock


def mock_data(mocker: MockerFixture) -> AppData:
    return mocker.patch("work_tracker.common.WorkData", autospec=True)


def sample_data() -> AppData:
    return AppData(
        country_code="PL"
    )


def generate_date() -> Date:
    start_date: datetime.date = datetime.date(1952, 1, 1)
    end_date: datetime.date = datetime.date(2049, 12, 31)
    day_offset: int = random.randint(0, (end_date - start_date).days)
    return Date.from_datetime(start_date + datetime.timedelta(days=day_offset))


def handle_call(
    handler: CommandHandler,
    dates: list[Date] = None,
    arguments: list[CommandArgument] = None,
    active_date: Date = None,
    mode: Mode = None,
    states: list[CommandHistoryEntry] = None,
    current_state_index: int = None
) -> CommandHandlerResult:
    dates = dates or []
    arguments = arguments or []
    if active_date is None and mode is None:
        active_date = generate_date().to_day_date()
        mode = Mode.Today
    elif active_date is not None and mode is None:
        if active_date.is_day_date():
            mode = Mode.Day
        elif active_date.is_month_date():
            mode = Mode.Month
    elif active_date is None and mode is not None:
        match mode:
            case Mode.Today | Mode.Day:
                active_date = generate_date().to_day_date()
            case Mode.Month:
                active_date = generate_date().to_month_date()
    states = states or []
    current_state_index = current_state_index or 0

    result: CommandHandlerResult = handler.handle(
        dates=dates,
        date_count=len(dates),
        arguments=arguments,
        argument_count=len(arguments),
        state=ReadonlyAppState(
            active_date=active_date,
            mode=mode,
            states=tuple(states),
            current_state_index=current_state_index
        )
    )

    return result


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    WorkTracker()._create_basic_files()


@pytest.fixture(autouse=True)
def reset_io_buffer():
    TestInputOutput.clear()


def get_fixture_params(request) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if hasattr(request, "param"):
        params = request.param if isinstance(request.param, dict) else {}
    return params


@pytest.fixture(scope="function")
def random_date(request) -> Date:
    params: dict[str, Any] = get_fixture_params(request)
    not_today: bool = params.get("not_today", False)
    must_be_workday: bool = params.get("must_be_workday", False)
    must_be_holiday: bool = params.get("must_be_holiday", False)
    country_code: str = params.get("country_code", "PL")

    while date := generate_date():
        if not_today and date == Date.today():
            continue
        if must_be_workday and not registry.get_calendars().get(country_code)().is_working_day(date.to_datetime()):
            continue
        if must_be_holiday and not registry.get_calendars().get(country_code)().is_holiday(date.to_datetime()):
            continue
        break
    return date


@pytest.fixture(scope="function")
def random_dates(request) -> list[Date]:
    params: dict[str, Any] = get_fixture_params(request)
    count: int = params.get("count", 5) # default count = 5
    unique_month_data: bool = params.get("unique_month_data", False)

    dates: list[Date] = []
    seen_month_years: set[tuple[int, int]] = set()
    for _ in range(count):
        while True:
            date: Date = generate_date()
            if unique_month_data:
                month_year: tuple[int, int] = (date.year, date.month)
                if month_year in seen_month_years:
                    continue
                seen_month_years.add(month_year)
            elif date in dates:
                continue
            break

        dates.append(date)

    return dates


@pytest.fixture(scope="function")
def internal_date_handler(mocker: MockerFixture):
    return _DateHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def internal_time_handler(mocker: MockerFixture):
    return _TimeHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def internal_macro_handler(mocker: MockerFixture):
    return _MacroHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def absence_handler(mocker: MockerFixture) -> AbsenceHandler:
    return AbsenceHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def alias_handler(mocker: MockerFixture) -> AliasHandler:
    return AliasHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def calendar_handler(mocker: MockerFixture) -> CalendarHandler:
    return CalendarHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def checkpoint_handler(mocker: MockerFixture) -> CheckpointHandler:
    return CheckpointHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def clear_handler(mocker: MockerFixture) -> ClearHandler:
    return ClearHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def config_handler(mocker: MockerFixture) -> ConfigHandler:
    return ConfigHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def dayoff_handler(mocker: MockerFixture) -> DayoffHandler:
    return DayoffHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def days_handler(mocker: MockerFixture) -> DaysHandler:
    return DaysHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def deletealias_handler(mocker: MockerFixture) -> DeletealiasHandler:
    return DeletealiasHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def deletemacro_handler(mocker: MockerFixture) -> DeletemacroHandler:
    return DeletemacroHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def done_handler(mocker: MockerFixture) -> DoneHandler:
    return DoneHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def end_handler(mocker: MockerFixture) -> EndHandler:
    return EndHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def exit_handler(mocker: MockerFixture) -> ExitHandler:
    return ExitHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def files_handler(mocker: MockerFixture) -> FilesHandler:
    return FilesHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def fte_handler(mocker: MockerFixture) -> FteHandler:
    return FteHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def help_handler(mocker: MockerFixture) -> HelpHandler:
    return HelpHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def history_handler(mocker: MockerFixture) -> HistoryHandler:
    return HistoryHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def holiday_handler(mocker: MockerFixture) -> HolidayHandler:
    return HolidayHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def info_handler(mocker: MockerFixture) -> InfoHandler:
    return InfoHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def key_handler(mocker: MockerFixture) -> KeyHandler:
    return KeyHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def keyword_handler(mocker: MockerFixture) -> KeywordHandler:
    return KeywordHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def macro_handler(mocker: MockerFixture) -> MacroHandler:
    return MacroHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def minutes_handler(mocker: MockerFixture) -> MinutesHandler:
    return MinutesHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def office_handler(mocker: MockerFixture) -> OfficeHandler:
    return OfficeHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def present_handler(mocker: MockerFixture) -> PresentHandler:
    return PresentHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def redo_handler(mocker: MockerFixture) -> RedoHandler:
    return RedoHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def remote_handler(mocker: MockerFixture) -> RemoteHandler:
    return RemoteHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def rollback_handler(mocker: MockerFixture) -> RollbackHandler:
    return RollbackHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def rwr_handler(mocker: MockerFixture) -> RwrHandler:
    return RwrHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def start_handler(mocker: MockerFixture) -> StartHandler:
    return StartHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def status_handler(mocker: MockerFixture) -> StatusHandler:
    return StatusHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def target_handler(mocker: MockerFixture) -> TargetHandler:
    return TargetHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def tutorial_handler(mocker: MockerFixture) -> TutorialHandler:
    return TutorialHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def undo_handler(mocker: MockerFixture) -> UndoHandler:
    return UndoHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def version_handler(mocker: MockerFixture) -> VersionHandler:
    return VersionHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def workday_handler(mocker: MockerFixture) -> WorkdayHandler:
    return WorkdayHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def zero_handler(mocker: MockerFixture) -> ZeroHandler:
    return ZeroHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )
