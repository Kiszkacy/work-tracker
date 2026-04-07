from prompt_toolkit.completion import Completion

from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument, CompletionCandidate, CompletionHint
from work_tracker.common import Date, ReadonlyAppState
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidArgumentValue, CommandErrorInvalidDateCount


class UndoHandler(CommandHandler):
    @classmethod
    def get_completions(cls, typed_words: list[str], last_word: str, in_subcommand_mode: bool) -> list[Completion | CompletionCandidate]:
        if len(typed_words) == 0:
            return cls.get_fitting_completions([CompletionCandidate(CompletionHint.Integer), CompletionCandidate(CompletionHint.Chain)], last_word)
        return []

    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count <= 1:
            count: int = arguments[0] if argument_count == 1 else 1
            if count <= 0:
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentValue(self.command_name, received_value=str(count), expected_value="a positive integer"))

            index: int = state.current_state_index
            history_size: int = len(state.states)
            if history_size == 0:
                self.io.output("No previous commands found to undo.")
                return CommandHandlerResult(undoable=False)
            elif index == 0:
                self.io.output("No more commands left to undo.")
                return CommandHandlerResult(undoable=False)

            steps: int = min(count, index)
            return CommandHandlerResult(undoable=False, change_state_by=-steps)
        elif date_count != 0:
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDateCount(self.command_name, received_date_count=date_count, expected_date_count=0))
        else: # argument_count > 1
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))
