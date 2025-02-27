import calendar
import re
from enum import Enum, auto

from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument
from work_tracker.common import Date, ReadonlyAppState, find_first_not_fulfilling
from work_tracker.config import Config, CalendarCommandConfig
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidDate, CommandErrorInvalidDateCount
from work_tracker.text.common import Color, frame_text


class CalendarDateType(Enum):
    Dayoff = auto()
    Holiday = auto()
    Office = auto()
    Remote = auto()
    Weekend = auto()


class CalendarHandler(CommandHandler):
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
            CalendarDateType.Dayoff: [date for date in month.days_in_a_month() if self.data.day[date].is_a_day_off],
            CalendarDateType.Holiday: [date for date in month.days_in_a_month() if not self.data.day[date].is_a_work_day and not date.to_datetime().isoweekday() in (6, 7)],
            CalendarDateType.Office: [date for date in month.days_in_a_month() if self.data.day[date].is_a_work_day and self.data.day[date].office_work and not self.data.day[date].is_a_day_off],
            CalendarDateType.Remote: [date for date in month.days_in_a_month() if self.data.day[date].is_a_work_day and self.data.day[date].remote_work and not self.data.day[date].is_a_day_off],
            CalendarDateType.Weekend: [date for date in month.days_in_a_month() if not self.data.day[date].is_a_work_day and date.to_datetime().isoweekday() in (6, 7)],
        }

    @staticmethod
    def _get_each_date_color() -> dict[CalendarDateType, str]:
        calendar_config: CalendarCommandConfig = Config.data.command.calendar

        return {
            CalendarDateType.Dayoff: CalendarHandler._get_color(calendar_config.dayoff_foreground_color, calendar_config.dayoff_background_color),
            CalendarDateType.Holiday: CalendarHandler._get_color(calendar_config.holiday_foreground_color, calendar_config.holiday_background_color),
            CalendarDateType.Office: CalendarHandler._get_color(calendar_config.office_foreground_color, calendar_config.office_background_color),
            CalendarDateType.Remote: CalendarHandler._get_color(calendar_config.remote_foreground_color, calendar_config.remote_background_color),
            CalendarDateType.Weekend: CalendarHandler._get_color(calendar_config.weekend_foreground_color, calendar_config.weekend_background_color),
        }

    @staticmethod
    def _get_color(foreground_key: str, background_key: str) -> str:
        fg_color: Color | None = Color.from_key(foreground_key)
        bg_color: Color | None = Color.from_key("bg_" + (background_key or ""))
        return (fg_color.value if fg_color else "") + (bg_color.value if bg_color else "")
