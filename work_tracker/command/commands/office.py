from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument
from work_tracker.common import Date, ReadonlyAppState, Mode, find_first_not_fulfilling
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidDate, CommandErrorInvalidMode


class OfficeHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 0:
            match state.mode:
                case Mode.Today | Mode.Day:
                    self._handle_day(state.active_date)
                    return CommandHandlerResult(undoable=True)
                case _:
                    return CommandHandlerResult(undoable=False, error=CommandErrorInvalidMode(self.command_name, mode=state.mode))
        elif date_count != 0 and argument_count == 0:
            if invalid_date := find_first_not_fulfilling(dates, lambda date: date.is_day_date()):
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDate(self.command_name, received_date=invalid_date))
            for date in dates:
                self._handle_day(date.fill_with(state.active_date))
            return CommandHandlerResult(undoable=True)
        else: # argument_count != 0
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))

    def _handle_day(self, date: Date):
        filled_date: Date = date.fill_with_today().to_day_date()
        self.data.day[filled_date].office_work = True
        self.data.day[filled_date].remote_work = False
