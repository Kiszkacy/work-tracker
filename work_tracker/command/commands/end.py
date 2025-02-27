import datetime

from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument, TimeArgument
from work_tracker.common import Date, ReadonlyAppState, Mode, Time, DayData
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidMode


class EndHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 0:
            match state.mode:
                case Mode.Today | Mode.Day:
                    pass
                case _:
                    return CommandHandlerResult(undoable=False, error=CommandErrorInvalidMode(self.command_name, mode=state.mode))

            time_now: datetime.datetime = datetime.datetime.now()
            day: DayData = self.data.day[state.active_date]
            day.work_end = Time(
                minutes_since_midnight=time_now.hour * 60 + time_now.minute
            )
            if day.work_start is not None:
                day.minutes_at_work = day.work_end.minutes_since_midnight - day.work_start.minutes_since_midnight
            return CommandHandlerResult(undoable=True)
        elif date_count == 0 and argument_count == 1: # TODO handle if end time is before start time
            match state.mode:
                case Mode.Today | Mode.Day:
                    pass
                case _:
                    return CommandHandlerResult(undoable=False, error=CommandErrorInvalidMode(self.command_name, mode=state.mode))

            time: TimeArgument = arguments[0]
            day: DayData = self.data.day[state.active_date]
            day.work_end = Time(
                minutes_since_midnight=time.minutes
            )
            if day.work_start is not None:
                day.minutes_at_work = day.work_end.minutes_since_midnight - day.work_start.minutes_since_midnight
            return CommandHandlerResult(undoable=True)
        else: # argument_count > 1
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))
