from fractions import Fraction

from prompt_toolkit.completion import Completion

import calendar as cal
from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument, CompletionCandidate
from work_tracker.common import Date, DayData, Mode, MonthData, ReadonlyAppState, DayType, WorkLocation, AttendanceType, find_first_not_fulfilling
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidDate, CommandErrorInvalidMode
from work_tracker.text.common import Color, frame_text


class InfoHandler(CommandHandler):
    @classmethod
    def get_completions(cls, typed_words: list[str], last_word: str, in_subcommand_mode: bool) -> list[Completion | CompletionCandidate]:
        return []

    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 0:
            match state.mode:
                case Mode.Today | Mode.Day:
                    self._handle_day(state.active_date)
                case Mode.Month:
                    self._handle_month(state.active_date)
                case _:
                    return CommandHandlerResult(undoable=False, error=CommandErrorInvalidMode(self.command_name, mode=state.mode))
            return CommandHandlerResult(undoable=False)
        elif date_count != 0 and argument_count == 0:
            if invalid_date := find_first_not_fulfilling(dates, lambda date: date.is_day_date() or date.is_month_date()):
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDate(self.command_name, received_date=invalid_date))
            for date in dates:
                if date.is_day_date():
                    self._handle_day(date.fill_with(state.active_date))
                elif date.is_month_date():
                    self._handle_month(date.fill_with(state.active_date))
            return CommandHandlerResult(undoable=False)
        else: # argument_count != 0
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))

    @staticmethod
    def _format_minutes(minutes: int) -> str: # TODO: move to a common file ?
        hours: int = int(minutes // 60)
        mins: int = int(minutes % 60)
        return f"{hours}:{mins:02}"

    @staticmethod
    def _format_time(minutes_since_midnight: int) -> str: # TODO: move to a common file ?
        hours: int = minutes_since_midnight // 60
        mins: int = minutes_since_midnight % 60
        return f"{hours}:{mins:02}"

    def _handle_day(self, date: Date):
        filled_date: Date = date.fill_with_today().to_day_date()
        day_data: DayData = self.data.day[filled_date]

        attendance_map: dict[AttendanceType, str] = {
            AttendanceType.PRESENT: "present",
            AttendanceType.DAYOFF: "day off",
            AttendanceType.ABSENCE: "absence",
        }
        day_type_map: dict[DayType, str] = {
            DayType.WORKDAY: "workday",
            DayType.WEEKEND: "weekend",
            DayType.HOLIDAY: "holiday",
        }
        location_map: dict[WorkLocation, str] = {
            WorkLocation.UNSPECIFIED: "unspecified",
            WorkLocation.REMOTE: "remote",
            WorkLocation.OFFICE: "office",
        }

        rows: list[tuple[str, str]] = [
            ("attendance", attendance_map.get(day_data.attendance_type, "unknown")),
            ("day type", day_type_map.get(day_data.day_type, "unknown")),
            ("work location", location_map.get(day_data.work_location, "unknown")),
            ("time at work", self._format_minutes(day_data.minutes_at_work)),
            ("target time", self._format_minutes(day_data.target_minutes)),
        ]
        if day_data.work_start is not None:
            rows.append(("work start", self._format_time(day_data.work_start.minutes_since_midnight)))
        if day_data.work_end is not None:
            rows.append(("work end", self._format_time(day_data.work_end.minutes_since_midnight)))
        
        longest_label: int = max(len(label) for label, _ in rows)
        separator: str = " | "
        lines: list[str] = [
            f"{Color.Brightblack.value if index % 2 == 1 else Color.Reset.value}{label.rjust(longest_label)}{separator}{Color.Brightcyan.value}{value}"
            for index, (label, value) in enumerate(rows)
        ]

        title: str = f"{filled_date.day:02}.{filled_date.month:02}.{filled_date.year}"
        framed_text: str = frame_text(text="\n".join(lines), title=title, title_color=Color.Bold)
        self.io.output(framed_text)

    def _handle_month(self, date: Date):
        filled_date: Date = date.fill_with_today().to_month_date()
        month_data: MonthData = self.data.month[filled_date]

        fte_text: str = "full-time" if month_data.fte == 1.0 else Fraction(month_data.fte).limit_denominator().__str__()

        if month_data.remote_work_ratio == 0:
            rwr_text: str = "office only"
        elif month_data.remote_work_ratio == 1:
            rwr_text: str = "remote only"
        else:
            rwr_text: str = Fraction(month_data.remote_work_ratio).limit_denominator().__str__()

        target_minutes_total: int = month_data.target_minutes
        target_minutes_office: int = int(target_minutes_total * (1.0 - month_data.remote_work_ratio))
        target_minutes_remote: int = int(target_minutes_total * month_data.remote_work_ratio)

        days_in_month: list[Date] = filled_date.days_in_a_month()
        working_days: int = sum(1 for day in days_in_month if self.data.day[day].day_type == DayType.WORKDAY)
        office_days: int = sum(1 for day in days_in_month if self.data.day[day].work_location == WorkLocation.OFFICE and self.data.day[day].attendance_type == AttendanceType.PRESENT)
        remote_days: int = sum(1 for day in days_in_month if self.data.day[day].work_location == WorkLocation.REMOTE and self.data.day[day].attendance_type == AttendanceType.PRESENT)
        office_days_total: int = sum(1 for day in days_in_month if self.data.day[day].work_location == WorkLocation.OFFICE)
        remote_days_total: int = sum(1 for day in days_in_month if self.data.day[day].work_location == WorkLocation.REMOTE)
        office_days_text: str = str(office_days) if office_days == office_days_total else f"{office_days} ({office_days_total} total)"
        remote_days_text: str = str(remote_days) if remote_days == remote_days_total else f"{remote_days} ({remote_days_total} total)"
        absent_days: int = sum(1 for day in days_in_month if self.data.day[day].attendance_type == AttendanceType.ABSENCE)
        day_offs: int = sum(1 for day in days_in_month if self.data.day[day].attendance_type == AttendanceType.DAYOFF)

        rows: list[tuple[str, str]] = [
            ("fte", fte_text),
            ("remote work ratio", rwr_text),
            ("target time", self._format_minutes(target_minutes_total)),
            ("target office time", self._format_minutes(target_minutes_office)),
            ("target remote time", self._format_minutes(target_minutes_remote)),
            ("working days", str(working_days)),
            ("office days", office_days_text),
            ("remote days", remote_days_text),
            ("absent days", str(absent_days)),
            ("day offs", str(day_offs)),
        ]

        longest_label: int = max(len(label) for label, _ in rows)
        separator: str = " | "
        lines: list[str] = [
            f"{Color.Brightblack.value if index % 2 == 1 else Color.Reset.value}{label.rjust(longest_label)}{separator}{Color.Brightcyan.value}{value}"
            for index, (label, value) in enumerate(rows)
        ]

        month_name: str = cal.month_name[filled_date.month]
        title: str = f"{month_name} {filled_date.year}"
        framed_text: str = frame_text(text="\n".join(lines), title=title, title_color=Color.Bold)
        self.io.output(framed_text)
