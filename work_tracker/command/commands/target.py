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
        if date_count == 0 and argument_count == 0:
            match state.mode:
                case Mode.Today | Mode.Day:
                    self._output_day_target(state.active_date)
                case Mode.Month:
                    self._output_month_target(state.active_date, ContextType.All)
                case _:
                    return CommandHandlerResult(undoable=False, error=CommandErrorInvalidMode(self.command_name, mode=state.mode))
            return CommandHandlerResult(undoable=False)
        elif date_count == 0 and argument_count == 1 and isinstance(arguments[0], TimeArgument):
            match state.mode:
                case Mode.Today | Mode.Day:
                    self._change_day_target(state.active_date, arguments[0].minutes)
                case Mode.Month:
                    self._change_month_target(state.active_date, arguments[0].minutes)
                case _:
                    return CommandHandlerResult(undoable=False, error=CommandErrorInvalidMode(self.command_name, mode=state.mode))
            return CommandHandlerResult(undoable=True)
        elif date_count == 0 and argument_count == 1 and isinstance(arguments[0], str):
            if not "office".startswith(arguments[0]) and not "remote".startswith(arguments[0]) and not "current".startswith(arguments[0]):
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentValue(self.command_name, received_value=arguments[0], expected_value=["office", "remote", "current"]))

            match state.mode:
                case Mode.Today | Mode.Day:
                    if "current".startswith(arguments[0]):
                        self._change_day_target(state.active_date, self.data.day[state.active_date].minutes_at_work)
                        return CommandHandlerResult(undoable=True)
                    else:
                        return CommandHandlerResult(undoable=False, error=CommandErrorInvalidMode(self.command_name, mode=state.mode, supported_modes={Mode.Month}))
                case Mode.Month:
                    if "current".startswith(arguments[0]):
                        return CommandHandlerResult(undoable=False, error=CommandErrorInvalidMode(self.command_name, mode=state.mode, supported_modes={Mode.Today, Mode.Day}))
                    else:
                        self._output_month_target(state.active_date, ContextType.Office if "office".startswith(arguments[0]) else ContextType.Remote)
                        return CommandHandlerResult(undoable=False)
                case _:
                    return CommandHandlerResult(undoable=False, error=CommandErrorInvalidMode(self.command_name, mode=state.mode))
        elif date_count != 0 and argument_count == 0:
            if invalid_date := find_first_not_fulfilling(dates, lambda date: date.is_day_date() or date.is_month_date()):
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDate(self.command_name, received_date=invalid_date))
            for date in dates:
                if date.is_day_date():
                    self._output_day_target(date.fill_with(state.active_date))
                elif date.is_month_date():
                    self._output_month_target(date.fill_with(state.active_date), ContextType.All)
            return CommandHandlerResult(undoable=False)
        elif date_count != 0 and argument_count == 1 and isinstance(arguments[0], TimeArgument):
            if invalid_date := find_first_not_fulfilling(dates, lambda date: date.is_day_date() or date.is_month_date()):
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDate(self.command_name, received_date=invalid_date))
            for date in dates:
                if date.is_day_date():
                    self._change_day_target(date.fill_with(state.active_date), arguments[0].minutes)
                elif date.is_month_date():
                    self._change_month_target(date.fill_with(state.active_date), arguments[0].minutes)
            return CommandHandlerResult(undoable=True)
        elif date_count != 0 and argument_count == 1 and isinstance(arguments[0], str):
            if not "office".startswith(arguments[0]) and not "remote".startswith(arguments[0]) and not "current".startswith(arguments[0]):
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentValue(self.command_name, received_value=arguments[0], expected_value=["office", "remote", "current"]))
            if "current".startswith(arguments[0]) and (invalid_date := find_first_not_fulfilling(dates, lambda date: date.is_day_date())):
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDate(self.command_name, received_date=invalid_date))
            elif not "current".startswith(arguments[0]) and (invalid_date := find_first_not_fulfilling(dates, lambda date: date.is_month_date())):
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDate(self.command_name, received_date=invalid_date))

            for date in dates:
                date = date.fill_with(state.active_date)
                if "current".startswith(arguments[0]):
                    self._change_day_target(date, self.data.day[date].minutes_at_work)
                    return CommandHandlerResult(undoable=True)
                else: # "office" or "remote"
                    self._output_month_target(date, ContextType.Office if "office".startswith(arguments[0]) else ContextType.Remote)
            return CommandHandlerResult(undoable=False)
        else: # argument_count > 1
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))

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
