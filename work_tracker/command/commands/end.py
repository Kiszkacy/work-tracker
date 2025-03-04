import datetime

from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument, TimeArgument
from work_tracker.common import Date, ReadonlyAppState, Mode, Time, DayData, find_first_not_fulfilling
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidMode, CommandErrorInvalidDate


class EndHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 0:
            match state.mode:
                case Mode.Today | Mode.Day:
                    pass
                case _:
                    return CommandHandlerResult(undoable=False, error=CommandErrorInvalidMode(self.command_name, mode=state.mode))

            self._handle_day(state.active_date)
            return CommandHandlerResult(undoable=True)
        elif date_count == 0 and argument_count == 1: # TODO handle if end time is before start time
            match state.mode:
                case Mode.Today | Mode.Day:
                    pass
                case _:
                    return CommandHandlerResult(undoable=False, error=CommandErrorInvalidMode(self.command_name, mode=state.mode))

            self._handle_day(state.active_date, arguments[0])
            return CommandHandlerResult(undoable=True)
        elif date_count != 0 and argument_count == 0:
            if invalid_date := find_first_not_fulfilling(dates, lambda date: date.is_day_date()):
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDate(self.command_name, received_date=invalid_date))
            for date in dates:
                self._handle_day(date.fill_with(state.active_date))
            return CommandHandlerResult(undoable=True)
        elif date_count != 0 and argument_count == 1:
            if invalid_date := find_first_not_fulfilling(dates, lambda date: date.is_day_date()):
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDate(self.command_name, received_date=invalid_date))
            for date in dates:
                self._handle_day(date.fill_with(state.active_date), arguments[0])
            return CommandHandlerResult(undoable=True)
        else:  # argument_count > 1
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))

    def _handle_day(self, date: Date, time: TimeArgument | None = None):
        date = date.fill_with_today().to_day_date()
        day: DayData = self.data.day[date]
        if time is not None:
            time_end: Time = Time(
                minutes_since_midnight=time.minutes
            )
        else:
            time_now: datetime.datetime = datetime.datetime.now()
            time_end: Time = Time(
                minutes_since_midnight=time_now.hour * 60 + time_now.minute
            )
        day.work_end = time_end

        if day.work_start is not None and day.work_start.minutes_since_midnight > day.work_end.minutes_since_midnight:
            day.work_start = time_end
            day.minutes_at_work = 0
        elif day.work_start is not None:
            day.minutes_at_work = day.work_end.minutes_since_midnight - day.work_start.minutes_since_midnight

        return CommandHandlerResult(undoable=True)
