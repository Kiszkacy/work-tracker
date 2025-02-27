from enum import Enum, auto

from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument, TimeArgument
from work_tracker.common import Date, ReadonlyAppState, Mode, find_first_not_fulfilling, MonthData
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidArgumentValue, CommandErrorInvalidDate, CommandErrorInvalidMode
from work_tracker.text.common import Color


class ContextType(Enum):
    All = auto(),
    Office = auto(),
    Remote = auto(),


class TargetHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if argument_count > 1:
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))
        initial_date_count: int = date_count
        if date_count != 0:
            if invalid_date := find_first_not_fulfilling(dates, lambda date: date.is_day_date() or date.is_month_date()):
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDate(self.command_name, received_date=invalid_date))
        else:
            match state.mode:
                case Mode.Today | Mode.Day | Mode.Month:
                    pass
                case _:
                    return CommandHandlerResult(undoable=False, error=CommandErrorInvalidMode(self.command_name, mode=state.mode))
            dates = [state.active_date]

        for date in dates:
            if argument_count == 0:
                if date.is_day_date():
                    self._output_day_target(date.fill_with(state.active_date))
                if date.is_month_date():
                    self._output_month_target(date.fill_with(state.active_date), ContextType.All)
            elif argument_count == 1 and isinstance(arguments[0], TimeArgument):
                if date.is_day_date():
                    self._change_day_target(date.fill_with(state.active_date), arguments[0].minutes)
                if date.is_month_date():
                    self._change_month_target(date.fill_with(state.active_date), arguments[0].minutes)
            elif argument_count == 1 and isinstance(arguments[0], str):
                if not "office".startswith(arguments[0]) and not "remote".startswith(arguments[0]) and not "current".startswith(arguments[0]):
                    return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentValue(self.command_name, received_value=arguments[0], expected_value=["office", "remote", "current"]))

                if date.is_day_date():
                    date = date.fill_with(state.active_date).to_day_date()
                    if "current".startswith(arguments[0]):
                        self._change_day_target(date, self.data.day[date].minutes_at_work)
                    elif initial_date_count == 0:
                        self._output_month_target(date.to_month_date(), ContextType.Office if "office".startswith(arguments[0]) else ContextType.Remote)
                    else:
                        # TODO this error can be misleading if user is providing a date (same with the error below)
                        # TODO possible solution: split the active date/given dates logic :(
                        return CommandHandlerResult(undoable=False, error=CommandErrorInvalidMode(self.command_name, mode=state.mode))
                elif date.is_month_date():
                    date = date.fill_with(state.active_date).to_month_date()
                    if "current".startswith(arguments[0]):
                        return CommandHandlerResult(undoable=False, error=CommandErrorInvalidMode(self.command_name, mode=state.mode))
                    else:
                        self._output_month_target(date, ContextType.Office if "office".startswith(arguments[0]) else ContextType.Remote)
        return CommandHandlerResult(undoable=True) # TODO return undoable=True only if target changed

    def _output_day_target(self, date: Date):
        date = date.fill_with_today().to_day_date()
        target_minutes: int = self.data.day[date].target_minutes
        hours: int = int(target_minutes // 60)
        minutes: int = int(target_minutes % 60)
        if hours == 0:
            self.io.output(f"{minutes} minutes", color=Color.Brightblue)
        else:
            self.io.output(f"{hours}:{minutes:02}", color=Color.Brightblue)

    def _output_month_target(self, date: Date, context: ContextType):
        date = date.fill_with_today().to_month_date()
        month: MonthData = self.data.month[date]

        total_minutes: float = 0.0
        match context:
            case ContextType.All:
                total_minutes = month.target_minutes
            case ContextType.Office:
                total_minutes = month.target_minutes * (1.0 - month.remote_work_ratio)
            case ContextType.Remote:
                total_minutes = month.target_minutes * month.remote_work_ratio

        hours: int = int(total_minutes // 60)
        minutes: int = int(total_minutes % 60)
        if hours == 0:
            self.io.output(f"{minutes} minutes", color=Color.Brightblue)
        else:
            self.io.output(f"{hours}:{minutes:02}", color=Color.Brightblue)

    def _change_day_target(self, date: Date, target_minutes: int):
        date = date.fill_with_today().to_day_date()
        self.data.day[date].target_minutes = target_minutes

    def _change_month_target(self, date: Date, target_minutes: int):
        date = date.fill_with_today().to_month_date()
        self.data.month[date].target_minutes = target_minutes
