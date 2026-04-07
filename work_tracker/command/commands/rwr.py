from fractions import Fraction

from prompt_toolkit.completion import Completion

from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument, CompletionCandidate, CompletionHint
from work_tracker.common import Date, DayType, ReadonlyAppState, Mode, find_first_not_fulfilling
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidDate, CommandErrorInvalidMode
from work_tracker.text.common import Color


class RwrHandler(CommandHandler):
    @classmethod
    def get_completions(cls, typed_words: list[str], last_word: str, in_subcommand_mode: bool) -> list[Completion | CompletionCandidate]:
        if len(typed_words) == 0:
            candidates = [CompletionCandidate("1", meta="full-time"), CompletionCandidate("4/5"), CompletionCandidate("3/5"), CompletionCandidate("1/2"), CompletionCandidate("2/5"), CompletionCandidate(CompletionHint.Chain)]
            return cls.get_fitting_completions(candidates, last_word)
        return []

    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 0:
            self._output_rwr(state.active_date)
            return CommandHandlerResult(undoable=False)
        elif date_count == 0 and argument_count == 1:
            match state.mode:
                case Mode.Today | Mode.Day | Mode.Month:
                    self._change_rwr(state.active_date, arguments[0])
                    return CommandHandlerResult(undoable=True)
                case _:
                    return CommandHandlerResult(undoable=False, error=CommandErrorInvalidMode(self.command_name, mode=state.mode))
        elif date_count != 0 and argument_count == 0:
            if invalid_date := find_first_not_fulfilling(dates, lambda date: date.is_day_date() or date.is_month_date()):
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDate(self.command_name, received_date=invalid_date))
            for date in dates:
                self._output_rwr(date.fill_with(state.active_date))
            return CommandHandlerResult(undoable=False)
        elif date_count != 0 and argument_count == 1:
            if invalid_date := find_first_not_fulfilling(dates, lambda date: date.is_day_date() or date.is_month_date()):
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDate(self.command_name, received_date=invalid_date))
            for date in dates:
                self._change_rwr(date.fill_with(state.active_date), arguments[0])
            return CommandHandlerResult(undoable=True)
        else: # argument_count > 1
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))

    def _output_rwr(self, date: Date):
        month: Date = date.fill_with_today().to_month_date()
        if self.data.month[month].remote_work_ratio == 0:
            self.io.output("office only", color=Color.Brightblue)
        elif self.data.month[month].remote_work_ratio == 1:
            self.io.output("remote only", color=Color.Brightblue)
        else:
            self.io.output(Fraction(self.data.month[month].remote_work_ratio).limit_denominator().__str__(), color=Color.Brightblue)

    def _change_rwr(self, date: Date, rwr: float):
        month: Date = date.fill_with_today().to_month_date()
        self.data.month[month].remote_work_ratio = rwr
        new_target_minutes_total: int = sum([480 * self.data.month[month].fte if self.data.day[day].day_type == DayType.WORKDAY else 0 for day in month.days_in_a_month()])
        self.data.month[month].target_minutes = new_target_minutes_total
