from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument
from work_tracker.common import Date, DayType, ReadonlyAppState, Mode, find_first_not_fulfilling
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidDate, CommandErrorInvalidMode


class HolidayHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 0:
            match state.mode:
                case Mode.Today | Mode.Day:
                    self._handle_day(state.active_date)
                    return CommandHandlerResult(undoable=True)
                case _:
                    return CommandHandlerResult(undoable=False, error=CommandErrorInvalidMode(self.command_name, mode=state.mode))
        elif date_count != 0 and argument_count == 0:
            if invalid_date := find_first_not_fulfilling(dates, lambda date: date.is_day_date()):
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDate(self.command_name, received_date=invalid_date))
            for date in dates:
                self._handle_day(date.fill_with(state.active_date))
            return CommandHandlerResult(undoable=True)
        else: # argument_count != 0
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))

    def _handle_day(self, date: Date):
        day_date: Date = date.fill_with_today().to_day_date()
        month_date: Date = date.fill_with_today().to_month_date()
        update_target_minutes = False

        if self._is_current_month_target_from_fte(month_date):
            update_target_minutes = True

        self.data.day[day_date].day_type = DayType.HOLIDAY

        if update_target_minutes:
            self._update_month_target_minutes(month_date)

    def _is_current_month_target_from_fte(self, month: Date) -> bool:
        return self.data.month[month].target_minutes == sum([480 * self.data.month[month].fte if self.data.day[day].day_type == DayType.WORKDAY else 0 for day in month.days_in_a_month()])

    def _update_month_target_minutes(self, month: Date):
        new_target_minutes_total: int = sum([480 * self.data.month[month].fte if self.data.day[day].day_type == DayType.WORKDAY else 0 for day in month.days_in_a_month()])
        self.data.month[month].target_minutes = new_target_minutes_total
