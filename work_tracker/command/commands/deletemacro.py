from prompt_toolkit.completion import Completion

from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument, CompletionCandidate
from work_tracker.command.macro_manager import MacroManager
from work_tracker.common import Date, ReadonlyAppState
from work_tracker.error import CommandErrorInvalidArgumentCount


class DeletemacroHandler(CommandHandler):
    @classmethod
    def get_completions(cls, typed_words: list[str], last_word: str, in_subcommand_mode: bool) -> list[Completion | CompletionCandidate]:
        if len(typed_words) == 0:
            return cls.get_fitting_completions([CompletionCandidate(name) for name in MacroManager.macros.keys()], last_word)
        return []

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

