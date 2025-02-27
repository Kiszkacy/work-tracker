from work_tracker.command.common import CommandArgument
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidDate, CommandErrorInvalidMode
from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.macro_manager import MacroManager
from work_tracker.common import Date, ReadonlyAppState, Mode, find_first_not_fulfilling


class DeletemacroHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 1:
            macro_identifier: str = arguments[0]
            if macro_identifier in MacroManager.macros:
                MacroManager.remove_macro(MacroManager.macros[macro_identifier])
                MacroManager.save_macros_file()
            else:
                self.io.output("Unknown macro.") # TODO
            return CommandHandlerResult(undoable=False)
        else: # argument_count != 1
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))

