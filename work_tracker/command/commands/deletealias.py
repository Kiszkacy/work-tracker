from prompt_toolkit.completion import Completion

from work_tracker.command.alias_manager import AliasManager
from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument, CompletionCandidate
from work_tracker.common import Date, ReadonlyAppState
from work_tracker.error import CommandErrorInvalidArgumentCount


class DeletealiasHandler(CommandHandler):
    @classmethod
    def get_completions(cls, typed_words: list[str], last_word: str, in_subcommand_mode: bool) -> list[Completion | CompletionCandidate]:
        if len(typed_words) == 0:
            return cls.get_fitting_completions([CompletionCandidate(name) for name in AliasManager.aliases.keys()], last_word)
        return []

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
