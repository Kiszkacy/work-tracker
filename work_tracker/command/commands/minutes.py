from enum import Enum, auto

from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument
from work_tracker.common import Date, ReadonlyAppState, find_first_not_fulfilling, Mode, MonthData
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidArgumentValue, CommandErrorInvalidDate, CommandErrorInvalidMode
from work_tracker.text.common import about_symbol, Color


class CalculateType(Enum):
    All = auto(),
    Office = auto(),
    Remote = auto(),


class MinutesHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if argument_count == 0 or argument_count > 3:
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))
        if date_count != 0:
            if invalid_date := find_first_not_fulfilling(dates, lambda date: date.is_month_date()):
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDate(self.command_name, received_date=invalid_date))
        else:
            match state.mode:
                case Mode.Today | Mode.Day | Mode.Month:
                    pass
                case _:
                    return CommandHandlerResult(undoable=False, error=CommandErrorInvalidMode(self.command_name, mode=state.mode))
            dates = [state.active_date]

        for date in dates:
            date = date.fill_with(state.active_date)
            if argument_count == 1:
                self._execute(date, arguments[0], CalculateType.All, take_into_account_filled_dates=True)
            elif argument_count == 2 and isinstance(arguments[0], str)  and isinstance(arguments[1], int): # minutes ('office'|'remote') <days>
                if not "office".startswith(arguments[0]) and not "remote".startswith(arguments[0]):
                    return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentValue(self.command_name, received_value=arguments[0], expected_value=["office", "remote"]))
                count_office_minutes: bool = "office".startswith(arguments[0])
                self._execute(date, arguments[1], CalculateType.Office if count_office_minutes else CalculateType.Remote, take_into_account_filled_dates=True)
            elif argument_count == 2 and isinstance(arguments[0], int) and isinstance(arguments[1], str): # minutes <days> ('clean')
                if not "clean".startswith(arguments[1]):
                    return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentValue(self.command_name, received_value=arguments[0], expected_value="clean"))
                self._execute(date, arguments[0], CalculateType.All, take_into_account_filled_dates=False)
            elif argument_count == 3: # minutes ('office'|'remote') <days> ('clean')
                if not "office".startswith(arguments[0]) and not "remote".startswith(arguments[0]):
                    return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentValue(self.command_name, received_value=arguments[0], expected_value=["office", "remote"]))
                if not "clean".startswith(arguments[2]):
                    return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentValue(self.command_name, received_value=arguments[0], expected_value="clean"))
                count_office_minutes: bool = "office".startswith(arguments[0])
                self._execute(date, arguments[1], CalculateType.Office if count_office_minutes else CalculateType.Remote, take_into_account_filled_dates=False)
        return CommandHandlerResult(undoable=False)
            
    def _execute(self, date: Date, day_count: int, calculate_type: CalculateType, take_into_account_filled_dates: bool):
        date = date.fill_with_today().to_month_date()
        month: MonthData = self.data.month[date.fill_with_today().to_month_date()]
        
        total_minutes: float = 0.0
        match calculate_type:
            case CalculateType.All:
                total_minutes = month.target_minutes
                if take_into_account_filled_dates:
                    total_minutes -= sum(self.data.day[day].minutes_at_work for day in date.days_in_a_month())
            case CalculateType.Office:
                total_minutes = month.target_minutes * (1.0 - month.remote_work_ratio)
                if take_into_account_filled_dates:
                    total_minutes -= sum(self.data.day[day].minutes_at_work for day in date.days_in_a_month() if self.data.day[day].office_work)
            case CalculateType.Remote:
                total_minutes = month.target_minutes * month.remote_work_ratio
                if take_into_account_filled_dates:
                    total_minutes -= sum(self.data.day[day].minutes_at_work for day in date.days_in_a_month() if self.data.day[day].remote_work)
        
        total_minutes_per_day: float = total_minutes / day_count
        rounded_total_minutes_per_day: int = round(total_minutes_per_day)
        is_exact_minute_count: bool = total_minutes_per_day.is_integer()

        hours: int = int(total_minutes_per_day // 60)
        minutes: int = int(total_minutes_per_day % 60)
        if hours == 0:
            self.io.write(f"{about_symbol if not is_exact_minute_count else ''}{rounded_total_minutes_per_day} minutes", color=Color.Brightblue, end=" ")
        else:
            self.io.write(f"{about_symbol if not is_exact_minute_count else ''}{hours}:{minutes:02}", color=Color.Brightblue, end=" ")
        self.io.write(f"each day", end=" ")
        self.io.write(f"({Color.Brightblue.value}{day_count}{Color.Reset.value} times)", end="")
        match calculate_type:
            case CalculateType.Office:
                self.io.output(f" {Color.Brightcyan.value}at office{Color.Reset.value}{'.' if take_into_account_filled_dates else ' excluding already filled dates.'}")
            case CalculateType.Remote:
                self.io.output(f" {Color.Brightcyan.value}remotely{Color.Reset.value}{'.' if take_into_account_filled_dates else ' excluding already filled dates.'}")
            case CalculateType.All:
                self.io.output(f"{'.' if take_into_account_filled_dates else ' excluding already filled dates.'}")
