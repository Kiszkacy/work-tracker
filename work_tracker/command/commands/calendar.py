import re
from enum import Enum, auto

from prompt_toolkit.completion import Completion

import calendar
from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument, CompletionCandidate
from work_tracker.common import Date, AttendanceType, DayType, WorkLocation, ReadonlyAppState, find_first_not_fulfilling
from work_tracker.config import Config, CalendarCommandConfig
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidDate, CommandErrorInvalidDateCount
from work_tracker.text.common import Color, frame_text


class CalendarDateType(Enum):
    Absence = auto()
    Dayoff = auto()
    Holiday = auto()
    Office = auto()
    IncompleteOffice = auto()
    Remote = auto()
    IncompleteRemote = auto()
    Weekend = auto()


class CalendarHandler(CommandHandler):
    @classmethod
    def get_completions(cls, typed_words: list[str], last_word: str, in_subcommand_mode: bool) -> list[Completion | CompletionCandidate]:
        return []

    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 0:
            self._display_calendar(state.active_date)
            return CommandHandlerResult(undoable=False)
        elif date_count != 0 and argument_count == 0:
            if invalid_date := find_first_not_fulfilling(dates, lambda date: date.is_month_date()):
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDate(self.command_name, received_date=invalid_date))
            for date in dates:
                self._display_calendar(date.fill_with_today())
            return CommandHandlerResult(undoable=False)
        elif date_count != 0:
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDateCount(self.command_name, received_date_count=date_count, expected_date_count=0))
        else: # argument_count != 0
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))

    def _display_calendar(self, date: Date):
        month: Date = date.to_month_date()
        text: str = self._get_calendar_text(month)
        framed_text: str = frame_text(
            text=f"{Color.from_key(Config.data.command.calendar.title_color).value if Config.data.command.calendar.title_color else ''}{text.rstrip()}"
        )
        self.io.output(framed_text)

    def _get_calendar_text(self, date: Date) -> str:
        month: Date = date.to_month_date()
        calendar_text: str = calendar.TextCalendar().formatmonth(month.year, month.month)

        dates: dict[CalendarDateType, list[Date]] = self._get_each_date_type_dates(month)
        colors: dict[CalendarDateType, str] = self._get_each_date_color()

        for date_type, dates_ in dates.items():
            for date in dates_:
                date_pattern = r'(?<=\s)' + re.escape(f"{date.day:2}") + r'(?=\s|\n)'
                colored_date = f"{colors[date_type]}{date.day:2}{Color.Clear.value}"
                calendar_text = re.sub(date_pattern, colored_date, calendar_text)

        # TODO ugly solution for todays date mark
        if Date.today().month == date.month and Date.today().year == date.year:
            date_pattern = re.escape(f"{Date.today().day:2}") + re.escape(Color.Clear.value)
            if re.search(date_pattern, calendar_text) is None: # if no color was given previously
                date_pattern = r'(?<=\s)' + re.escape(f"{Date.today().day:2}") + r'(?=\s|\n)'
            colored_date = f"{Color.Underline.value}{Date.today().day:2}{Color.Clear.value}"
            calendar_text = re.sub(date_pattern, colored_date, calendar_text)
       
        special_dates: set[Date] = set(sum([dates_ for _, dates_ in dates.items()], [])) # flatmap
        all_dates: set[Date] = set(Date.days_in_a_month(month))
        default_dates: list[Date] = list(all_dates.difference(special_dates))
        for date in default_dates:
            date_pattern = r'(?<=\s)' + re.escape(f"{date.day:2}") + r'(?=\s|\n)'
            colored_date = f"{Color.Clear.value}{date.day:2}"
            calendar_text = re.sub(date_pattern, colored_date, calendar_text)

        return calendar_text

    def _get_each_date_type_dates(self, month: Date) -> dict[CalendarDateType, list[Date]]:
        return {
            CalendarDateType.Absence: [date for date in month.days_in_a_month() if self.data.day[date].attendance_type == AttendanceType.ABSENCE],
            CalendarDateType.Dayoff: [date for date in month.days_in_a_month() if self.data.day[date].attendance_type == AttendanceType.DAYOFF],
            CalendarDateType.IncompleteOffice: [date for date in month.days_in_a_month() if self.data.day[date].work_location == WorkLocation.OFFICE and (self.data.day[date].minutes_at_work < self.data.day[date].target_minutes or self.data.day[date].target_minutes == 0)],
            CalendarDateType.Office: [date for date in month.days_in_a_month() if self.data.day[date].work_location == WorkLocation.OFFICE],
            CalendarDateType.IncompleteRemote: [date for date in month.days_in_a_month() if self.data.day[date].work_location == WorkLocation.REMOTE and (self.data.day[date].minutes_at_work < self.data.day[date].target_minutes or self.data.day[date].target_minutes == 0)],
            CalendarDateType.Remote: [date for date in month.days_in_a_month() if self.data.day[date].work_location == WorkLocation.REMOTE],
            CalendarDateType.Holiday: [date for date in month.days_in_a_month() if self.data.day[date].day_type == DayType.HOLIDAY],
            CalendarDateType.Weekend: [date for date in month.days_in_a_month() if self.data.day[date].day_type == DayType.WEEKEND],
        }

    @staticmethod
    def _get_each_date_color() -> dict[CalendarDateType, str]:
        calendar_config: CalendarCommandConfig = Config.data.command.calendar

        return {
            CalendarDateType.Absence: CalendarHandler._get_color(calendar_config.absence_foreground_color, calendar_config.absence_background_color),
            CalendarDateType.Dayoff: CalendarHandler._get_color(calendar_config.dayoff_foreground_color, calendar_config.dayoff_background_color),
            CalendarDateType.IncompleteOffice: CalendarHandler._get_color(calendar_config.office_incomplete_foreground_color, calendar_config.office_incomplete_background_color),
            CalendarDateType.Office: CalendarHandler._get_color(calendar_config.office_foreground_color, calendar_config.office_background_color),
            CalendarDateType.IncompleteRemote: CalendarHandler._get_color(calendar_config.remote_incomplete_foreground_color, calendar_config.remote_incomplete_background_color),
            CalendarDateType.Remote: CalendarHandler._get_color(calendar_config.remote_foreground_color, calendar_config.remote_background_color),
            CalendarDateType.Holiday: CalendarHandler._get_color(calendar_config.holiday_foreground_color, calendar_config.holiday_background_color),
            CalendarDateType.Weekend: CalendarHandler._get_color(calendar_config.weekend_foreground_color, calendar_config.weekend_background_color),
        }

    @staticmethod
    def _get_color(foreground_key: str, background_key: str) -> str:
        fg_color: Color | None = Color.from_key(foreground_key)
        bg_color: Color | None = Color.from_key("bg_" + (background_key or ""))
        return (fg_color.value if fg_color else "") + (bg_color.value if bg_color else "")
