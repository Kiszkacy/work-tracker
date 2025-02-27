from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument
from work_tracker.common import Date, ReadonlyAppState
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidDateCount


class UndoHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 0:
            index: int = state.current_state_index
            history_size: int = len(state.states)
            if history_size == 0:
                self.io.output("No previous commands found to undo.")
                return CommandHandlerResult(undoable=False)
            elif index == 0:
                self.io.output("No more commands left to undo.")
                return CommandHandlerResult(undoable=False)
            return CommandHandlerResult(undoable=False, change_state_by=-1)
        elif date_count != 0:
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDateCount(self.command_name, received_date_count=date_count, expected_date_count=0))
        else: # argument_count != 0
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))
