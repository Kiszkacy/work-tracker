from work_tracker.command.common import CommandArgument
from work_tracker.error import CommandErrorInvalidArgumentCount
from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.alias_manager import AliasManager
from work_tracker.common import Date, ReadonlyAppState


class DeletealiasHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 1:
            alias_identifier: str = arguments[0]
            if alias_identifier in AliasManager.aliases:
                AliasManager.remove_alias(AliasManager.aliases[alias_identifier])
                AliasManager.save_aliases_file()
            else:
                self.io.output("Unknown alias.") # TODO
            return CommandHandlerResult(undoable=False)
        else: # argument_count != 1
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))
