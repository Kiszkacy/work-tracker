from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument
from work_tracker.common import Date, ReadonlyAppState, Mode, find_first_not_fulfilling
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidDate, CommandErrorInvalidMode


class ClearHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 0:
            match state.mode:
                case Mode.Today | Mode.Day:
                    self._handle_day(state.active_date)
                case Mode.Month:
                    self._handle_month(state.active_date)
                case _:
                    return CommandHandlerResult(undoable=False, error=CommandErrorInvalidMode(self.command_name, mode=state.mode))
            return CommandHandlerResult(undoable=True)
        elif date_count != 0 and argument_count == 0:
            if invalid_date := find_first_not_fulfilling(dates, lambda date: date.is_day_date() or date.is_month_date()):
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDate(self.command_name, received_date=invalid_date))

            for date in dates:
                if date.is_day_date():
                    self._handle_day(date.fill_with(state.active_date))
                elif date.is_month_date():
                    self._handle_month(date.fill_with(state.active_date))
            return CommandHandlerResult(undoable=True)
        else: # argument_count != 0
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))

    def _handle_day(self, date: Date):
        date = date.fill_with_today().to_day_date()
        self.data.day[date].reset(is_a_work_day=self.data.calendar.is_working_day(date.to_datetime()))

    def _handle_month(self, date: Date):
        date = date.fill_with_today().to_month_date()
        for day in date.days_in_a_month():
            self.data.day[day].reset(is_a_work_day=self.data.calendar.is_working_day(day.to_datetime()))
        self.data.month[date].fte = self.data.setup.default_fte
        self.data.month[date].remote_work_ratio = self.data.setup.default_remote_work_ratio
        new_target_minutes_total: int = sum([480 * self.data.month[date].fte if self.data.day[day].is_a_work_day else 0 for day in date.days_in_a_month()])
        self.data.month[date].target_minutes = new_target_minutes_total
