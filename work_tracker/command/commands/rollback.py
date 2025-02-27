from work_tracker.checkpoint_manager import CheckpointManager
from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument
from work_tracker.common import Date, ReadonlyAppState, AppData
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidDateCount


class RollbackHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 1:
            checkpoint_identifier: str = arguments[0]
            data: AppData = CheckpointManager.load(checkpoint_identifier, manual_checkpoint=True)
            if data is None:
                self.io.output(f"Could not find a checkpoint named {checkpoint_identifier}.")
                return CommandHandlerResult(undoable=False)
            self.data.copy_from(data)
            return CommandHandlerResult(undoable=True)
        elif date_count != 0:
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDateCount(self.command_name, received_date_count=date_count, expected_date_count=0))
        else: # argument_count != 0
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))
