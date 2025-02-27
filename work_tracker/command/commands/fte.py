from fractions import Fraction

from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument
from work_tracker.common import Date, ReadonlyAppState, Mode, find_first_not_fulfilling
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidDate, CommandErrorInvalidMode
from work_tracker.text.common import Color


class FteHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 0:
            self._output_fte(state.active_date)
            return CommandHandlerResult(undoable=False)
        elif date_count == 0 and argument_count == 1:
            match state.mode:
                case Mode.Today | Mode.Day | Mode.Month:
                    self._change_fte(state.active_date, arguments[0])
                    return CommandHandlerResult(undoable=True)
                case _:
                    return CommandHandlerResult(undoable=False, error=CommandErrorInvalidMode(self.command_name, mode=state.mode))
        elif date_count != 0 and argument_count == 0:
            if invalid_date := find_first_not_fulfilling(dates, lambda date: date.is_month_date()):
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDate(self.command_name, received_date=invalid_date))
            for date in dates:
                self._output_fte(date.fill_with(state.active_date))
            return CommandHandlerResult(undoable=False)
        elif date_count != 0 and argument_count == 1:
            if invalid_date := find_first_not_fulfilling(dates, lambda date: date.is_month_date()):
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDate(self.command_name, received_date=invalid_date))
            for date in dates:
                self._change_fte(date.fill_with(state.active_date), arguments[0])
            return CommandHandlerResult(undoable=True)
        else: # argument_count > 1
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))

    def _output_fte(self, date: Date):
        month: Date = date.fill_with_today().to_month_date()
        if self.data.month[month].fte == 1:
            self.io.output("full-time", color=Color.Brightblue)
        else:
            self.io.output(Fraction(self.data.month[month].fte).limit_denominator().__str__(), color=Color.Brightblue)

    def _change_fte(self, date: Date, fte: float):
        month: Date = date.fill_with_today().to_month_date()
        self.data.month[month].fte = fte
        new_target_minutes_total: int = sum([480 * self.data.month[month].fte if self.data.day[day].is_a_work_day else 0 for day in month.days_in_a_month()])
        self.data.month[month].target_minutes = new_target_minutes_total
