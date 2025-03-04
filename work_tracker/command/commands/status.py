from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument
from work_tracker.common import Date, ReadonlyAppState, Mode, find_first_not_fulfilling
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidDate, CommandErrorInvalidMode, CommandErrorInvalidDateCount
from work_tracker.text.common import Color


class StatusHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 0:
            match state.mode:
                case Mode.Today | Mode.Day:
                    self._handle_day(state.active_date)
                case Mode.Month:
                    self._handle_month(state.active_date)
                case _:
                    return CommandHandlerResult(undoable=False, error=CommandErrorInvalidMode(self.command_name, mode=state.mode))
            return CommandHandlerResult(undoable=False)
        elif date_count != 0 and argument_count == 0:
            if invalid_date := find_first_not_fulfilling(dates, lambda date: date.is_day_date() or date.is_month_date()):
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDate(self.command_name, received_date=invalid_date))

            for date in dates:
                if date.is_day_date():
                    self._handle_day(date.fill_with(state.active_date))
                elif date.is_month_date():
                    self._handle_month(date.fill_with(state.active_date))
            return CommandHandlerResult(undoable=False)
        elif date_count == 0:
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDateCount(self.command_name, received_date_count=date_count, expected_date_count=0))
        else: # argument_count != 0
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))

    def _handle_day(self, date: Date):
        date = date.fill_with_today().to_day_date()

        minutes_at_work: int = self.data.day[date].minutes_at_work
        target_minutes: int = self.data.day[date].target_minutes
        hours: int = int(minutes_at_work // 60)
        minutes: int = int(minutes_at_work % 60)
        target_hours: int = int(target_minutes // 60)
        target_minutes: int = int(target_minutes % 60)
        if target_hours == 0 and hours == 0:
            self.io.write(f"{minutes} minutes", color=Color.Brightblue, end=" ")
        else:
            self.io.write(f"{hours}:{minutes:02}", color=Color.Brightblue, end="")
        self.io.write("/", end="")
        if target_hours == 0 and hours == 0:
            self.io.output(f" {target_minutes} minutes", color=Color.Blue)
        else:
            self.io.output(f"{target_hours}:{target_minutes:02}", color=Color.Blue)

    def _handle_month(self, date: Date):
        date = date.fill_with_today().to_day_date()
        minutes_at_work_office: int = sum([self.data.day[day].minutes_at_work for day in date.days_in_a_month() if self.data.day[day].office_work])
        minutes_at_work_remote: int = sum([self.data.day[day].minutes_at_work for day in date.days_in_a_month() if self.data.day[day].remote_work])
        month: Date = date.to_month_date()
        target_minutes_total: int = self.data.month[month].target_minutes
        target_minutes_office: int = int(target_minutes_total * (1.0 - self.data.month[month].remote_work_ratio))
        target_minutes_remote: int = int(target_minutes_total * self.data.month[month].remote_work_ratio)

        if target_minutes_office != 0:
            hours: int = int(minutes_at_work_office // 60)
            minutes: int = int(minutes_at_work_office % 60)
            target_hours: int = int(target_minutes_office // 60)
            target_minutes: int = int(target_minutes_office % 60)

            if target_hours == 0 and hours == 0:
                self.io.write(f"{minutes} minutes", color=Color.Brightblue, end=" ")
            else:
                self.io.write(f"{hours}:{minutes:02}", color=Color.Brightblue, end="")
            self.io.write("/", end="")
            if target_hours == 0 and hours == 0:
                self.io.write(f" {target_minutes} minutes", color=Color.Blue, end=" ")
            else:
                self.io.write(f"{target_hours}:{target_minutes:02}", color=Color.Blue, end=" ")
            self.io.output(f"{Color.Brightcyan.value}at office{Color.Reset.value}.")
        if target_minutes_remote != 0:
            hours: int = int(minutes_at_work_remote // 60)
            minutes: int = int(minutes_at_work_remote % 60)
            target_hours: int = int(target_minutes_remote // 60)
            target_minutes: int = int(target_minutes_remote % 60)
            if target_hours == 0 and hours == 0:
                self.io.write(f"{minutes} minutes", color=Color.Brightblue, end=" ")
            else:
                self.io.write(f"{hours}:{minutes:02}", color=Color.Brightblue, end="")
            self.io.write("/", end="")
            if target_hours == 0 and hours == 0:
                self.io.write(f" {target_minutes} minutes", color=Color.Blue, end=" ")
            else:
                self.io.write(f"{target_hours}:{target_minutes:02}", color=Color.Blue, end=" ")
            self.io.output(f"{Color.Brightcyan.value}remotely{Color.Reset.value}.")