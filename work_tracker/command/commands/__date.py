from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument
from work_tracker.common import Date, ReadonlyAppState
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidDate, CommandErrorInvalidDateCount


class __DateHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if argument_count == 0 and date_count == 1:
            date: Date = dates[0]
            if date.is_day_date():
                day: Date = date.fill_with(state.active_date).fill_with_today().to_day_date()
                return CommandHandlerResult(undoable=False, change_active_date=day)
            elif date.is_month_date():
                month: Date = date.fill_with(state.active_date).fill_with_today().to_month_date()
                return CommandHandlerResult(undoable=False, change_active_date=month)
            else:
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDate(self.command_name, received_date=date))
        elif date_count != 1:
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDateCount(self.command_name, received_date_count=date_count, expected_date_count=1))
        else:
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))
