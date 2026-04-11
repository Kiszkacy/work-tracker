from prompt_toolkit.completion import Completion

from workalendar.registry import registry

from work_tracker.checkpoint_manager import CheckpointManager
from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument, CompletionCandidate
from work_tracker.common import Date, ReadonlyAppState
from work_tracker.error import CommandErrorInvalidArgumentCount
from work_tracker.text.common import Color


class CountryHandler(CommandHandler):
    @classmethod
    def get_completions(cls, typed_words: list[str], last_word: str, in_subcommand_mode: bool) -> list[Completion | CompletionCandidate]:
        if len(typed_words) == 0:
            return cls.get_fitting_completions([CompletionCandidate(code, meta=calendar.name) for code, calendar in sorted(registry.get_calendars().items())], last_word)
        return []

    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 0:
            self.io.output(self.data.country_code, color=Color.Brightblue)
            return CommandHandlerResult(undoable=False)
        elif date_count == 0 and argument_count == 1:
            new_code: str = str(arguments[0]).upper()
            valid_codes: list[str] = sorted(registry.get_calendars().keys())
            if new_code not in valid_codes:
                self.io.output(f"Invalid country code {Color.Brightred.value}{new_code}{Color.Reset.value}. Use tab-completion or type a valid ISO country code.")
                return CommandHandlerResult(undoable=False)
            if new_code == self.data.country_code:
                self.io.output(f"Country code is already set to {Color.Brightblue.value}{new_code}{Color.Reset.value}.")
                return CommandHandlerResult(undoable=False)
            self.data.change_country_code(new_code)
            CheckpointManager.save("country", self.data, add_suffix_timestamp=True)
            self.io.output(f"Country code changed to {Color.Brightblue.value}{new_code}{Color.Reset.value}.")
            return CommandHandlerResult(undoable=True)
        else:
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))
