import sys

from prompt_toolkit.completion import Completion
from work_tracker.command.common import CommandArgument, CompletionCandidate
from work_tracker.error import CommandErrorInvalidArgumentCount
from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.common import Date, ReadonlyAppState, Mode
from work_tracker.checkpoint_manager import CheckpointManager


class ExitHandler(CommandHandler):
    @classmethod
    def get_completions(cls, typed_words: list[str], last_word: str, in_subcommand_mode: bool) -> list[Completion | CompletionCandidate]:
        return []

    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 0:
            if state.mode != Mode.Today:
                return CommandHandlerResult(undoable=False, change_active_date=Date.today())
            else:
                CheckpointManager.save("exit", self.data, add_suffix_timestamp=True)
                sys.exit()
        else: # argument_count != 0
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))
