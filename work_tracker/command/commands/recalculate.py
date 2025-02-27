from work_tracker.command.common import CommandArgument
from work_tracker.error import CommandErrorNotImplemented
from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.common import Date, ReadonlyAppState


class RecalculateHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        return CommandHandlerResult(undoable=False, error=CommandErrorNotImplemented(command_name=self.command_name))
