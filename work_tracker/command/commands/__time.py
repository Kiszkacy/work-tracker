from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument, TimeArgument, TimeArgumentType
from work_tracker.common import Date, ReadonlyAppState, find_first_not_fulfilling
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidDate, CommandErrorInvalidDateCount


class __TimeHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if argument_count == 1:
            if len(dates) == 0:
                dates = [state.active_date]

            if invalid_date := find_first_not_fulfilling(dates, lambda date: date.is_day_date() or date.is_month_date()):
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDate(self.command_name, received_date=invalid_date))

            for date in dates:
                if date.is_day_date():
                    day: Date = date.fill_with(state.active_date).fill_with_today().to_day_date()
                    time_data: TimeArgument = arguments[0]
                    was_worktime_target_equal: bool = self.data.day[day].target_minutes == self.data.day[day].minutes_at_work
                    match time_data.type:
                        case TimeArgumentType.Overwrite:
                            self.data.day[day].minutes_at_work = time_data.minutes
                        case TimeArgumentType.Add:
                            self.data.day[day].minutes_at_work += time_data.minutes
                        case TimeArgumentType.Subtract:
                            self.data.day[day].minutes_at_work -= time_data.minutes
                    if self.data.day[day].target_minutes < self.data.day[day].minutes_at_work or was_worktime_target_equal: # TODO inform about this user
                        self.data.day[day].target_minutes = self.data.day[day].minutes_at_work
                elif date.is_month_date():
                    month: Date = date.fill_with(state.active_date).fill_with_today().to_month_date()
                    time_data: TimeArgument = arguments[0]
                    new_target_minutes: int = time_data.minutes
                    match time_data.type:
                        case TimeArgumentType.Overwrite:
                            self.data.month[month].target_minutes = new_target_minutes
                        case TimeArgumentType.Add:
                            self.data.month[month].target_minutes += new_target_minutes
                        case TimeArgumentType.Subtract:
                            self.data.month[month].target_minutes -= new_target_minutes
                    # TODO this changes the target minute count but doesnt change fte, that is by design but user should be aware of this when printing month data, right now
                    # TODO there isnt any indication about that
                # add year mode if needed here
            return CommandHandlerResult(undoable=True)
        elif date_count != 0:
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDateCount(self.command_name, received_date_count=date_count, expected_date_count=0))
        else: # argument_count != 0
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))
