from prompt_toolkit.completion import Completion

import dataclasses

from work_tracker.command.clipboard import Clipboard
from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument, CompletionCandidate, CompletionHint
from work_tracker.common import Date, ReadonlyAppState, Mode
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidDate, CommandErrorInvalidMode, CommandErrorInvalidDateCount


class CopyHandler(CommandHandler):
    @classmethod
    def get_completions(cls, typed_words: list[str], last_word: str, in_subcommand_mode: bool) -> list[Completion | CompletionCandidate]:
        if len(typed_words) == 0:
            return cls.get_fitting_completions([CompletionCandidate(CompletionHint.Chain)], last_word)
        return []

    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 0:
            match state.mode:
                case Mode.Today | Mode.Day:
                    pass
                case _:
                    return CommandHandlerResult(undoable=False, error=CommandErrorInvalidMode(self.command_name, mode=state.mode))
            self._handle_day(state.active_date)
            return CommandHandlerResult(undoable=False)
        elif date_count == 1 and argument_count == 0:
            if not dates[0].is_day_date():
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDate(self.command_name, received_date=dates[0]))
            self._handle_day(dates[0].fill_with(state.active_date))
            return CommandHandlerResult(undoable=False)
        elif date_count > 1 and argument_count == 0:
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDateCount(self.command_name, received_date_count=date_count, expected_date_count=1))
        else:
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))

    def _handle_day(self, date: Date):
        filled_date: Date = date.fill_with_today().to_day_date()
        Clipboard.set(Clipboard.COPY_PASTE_KEY, dataclasses.replace(self.data.day[filled_date])) # shallow copy
