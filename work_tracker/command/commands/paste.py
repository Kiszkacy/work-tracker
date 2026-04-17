from prompt_toolkit.completion import Completion

from work_tracker.command.clipboard import Clipboard
from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument, CompletionCandidate, CompletionHint
from work_tracker.common import Date, DayData, ReadonlyAppState, Mode, find_first_not_fulfilling
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidDate, CommandErrorInvalidMode, CommandErrorCustom


class PasteHandler(CommandHandler):
    @classmethod
    def get_completions(cls, typed_words: list[str], last_word: str, in_subcommand_mode: bool) -> list[Completion | CompletionCandidate]:
        if len(typed_words) == 0:
            return cls.get_fitting_completions([CompletionCandidate(CompletionHint.Chain)], last_word)
        return []

    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if argument_count != 0:
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))

        if not Clipboard.has(Clipboard.COPY_PASTE_KEY):
            return CommandHandlerResult(undoable=False, error=CommandErrorCustom(self.command_name, custom_message="clipboard is empty, use 'copy' first."))

        if date_count == 0:
            match state.mode:
                case Mode.Today | Mode.Day:
                    pass
                case _:
                    return CommandHandlerResult(undoable=False, error=CommandErrorInvalidMode(self.command_name, mode=state.mode))
            self._handle_day(state.active_date)
            return CommandHandlerResult(undoable=True)
        else:
            if invalid_date := find_first_not_fulfilling(dates, lambda date: date.is_day_date()):
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDate(self.command_name, received_date=invalid_date))
            for date in dates:
                self._handle_day(date.fill_with(state.active_date))
            return CommandHandlerResult(undoable=True)

    def _handle_day(self, date: Date):
        filled_date: Date = date.fill_with_today().to_day_date()
        source: DayData = Clipboard.get(Clipboard.COPY_PASTE_KEY)
        target: DayData = self.data.day[filled_date]
        
        target.attendance_type = source.attendance_type
        target.day_type = source.day_type
        target.work_location = source.work_location
        target.minutes_at_work = source.minutes_at_work
        target.target_minutes = source.target_minutes
        target.work_start = source.work_start
        target.work_end = source.work_end
