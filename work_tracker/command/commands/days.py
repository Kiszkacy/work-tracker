from enum import Enum, auto

from prompt_toolkit.completion import Completion

from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument, TimeArgument, CompletionHint, CompletionCandidate
from work_tracker.common import Date, WorkLocation, ReadonlyAppState, find_first_not_fulfilling, Mode, MonthData
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidArgumentValue, CommandErrorInvalidDate, CommandErrorInvalidMode
from work_tracker.text.common import about_symbol, Color


class CalculateType(Enum):
    All = auto(),
    Office = auto(),
    Remote = auto(),


class CommandCallType(Enum):
    MINUTES_ONLY = auto(),
    CLEAN_MINUTES = auto(),
    OFFICE_OR_REMOTE_MINUTES = auto(),
    OFFICE_OR_REMOTE_CLEAN_MINUTES = auto(),


class DaysHandler(CommandHandler):
    @classmethod
    def get_completions(cls, typed_words: list[str], last_word: str, in_subcommand_mode: bool) -> list[Completion | CompletionCandidate]:
        is_work_type_provided: bool = len(typed_words) > 0 and ("office".startswith(typed_words[0]) or "remote".startswith(typed_words[0]))

        if len(typed_words) == 0:
            candidates = [CompletionCandidate("office"), CompletionCandidate("remote"), CompletionCandidate(CompletionHint.Time)]
        elif len(typed_words) == 1:
            candidates = [CompletionCandidate(CompletionHint.Time)] if is_work_type_provided else [CompletionCandidate("clean")]
        elif len(typed_words) == 2 and is_work_type_provided:
            candidates = [CompletionCandidate("clean")]
        else:
            return []
        return cls.get_fitting_completions(candidates, last_word)

    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        call_type: CommandCallType = None
        
        if argument_count == 1:
            call_type = CommandCallType.MINUTES_ONLY
            if arguments[0].minutes <= 0:
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentValue(self.command_name, received_value=arguments[0], expected_value="value bigger than 0"))
        elif argument_count == 2 and isinstance(arguments[0], str) and isinstance(arguments[1], TimeArgument): # days ('office'|'remote') <minutes>
            call_type = CommandCallType.OFFICE_OR_REMOTE_MINUTES
            if arguments[1].minutes <= 0:
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentValue(self.command_name, received_value=arguments[1], expected_value="value bigger than 0"))
        elif argument_count == 2 and isinstance(arguments[0], TimeArgument) and isinstance(arguments[1], str): # days <minutes> ('clean')
            call_type = CommandCallType.CLEAN_MINUTES
            if arguments[0].minutes <= 0:
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentValue(self.command_name, received_value=arguments[0], expected_value="value bigger than 0"))
        elif argument_count == 3: # days ('office'|'remote') <minutes> ('clean')
            call_type = CommandCallType.OFFICE_OR_REMOTE_CLEAN_MINUTES
            if arguments[1].minutes <= 0:
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentValue(self.command_name, received_value=arguments[1], expected_value="value bigger than 0"))
        else: # argument_count == 0 or argument_count > 3
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))
            
        if date_count != 0:
            if invalid_date := find_first_not_fulfilling(dates, lambda date: date.is_day_date() or date.is_month_date()):
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDate(self.command_name, received_date=invalid_date))
        else:
            match state.mode:
                case Mode.Today | Mode.Day | Mode.Month:
                    pass
                case _:
                    return CommandHandlerResult(undoable=False, error=CommandErrorInvalidMode(self.command_name, mode=state.mode))
            dates = [state.active_date]

        for date in dates:
            date = date.fill_with(state.active_date)
            match call_type:
                case CommandCallType.MINUTES_ONLY:
                    self._execute(date, arguments[0].minutes, CalculateType.All, take_into_account_filled_dates=True)
                case CommandCallType.OFFICE_OR_REMOTE_MINUTES:
                    if not "office".startswith(arguments[0]) and not "remote".startswith(arguments[0]):
                        return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentValue(self.command_name, received_value=arguments[0], expected_value=["office", "remote"]))
                    count_office_minutes: bool = "office".startswith(arguments[0])
                    self._execute(date, arguments[1].minutes, CalculateType.Office if count_office_minutes else CalculateType.Remote, take_into_account_filled_dates=True)
                case CommandCallType.CLEAN_MINUTES:
                    if not "clean".startswith(arguments[1]):
                        return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentValue(self.command_name, received_value=arguments[1], expected_value="clean"))
                    self._execute(date, arguments[0].minutes, CalculateType.All, take_into_account_filled_dates=False)
                case CommandCallType.OFFICE_OR_REMOTE_CLEAN_MINUTES:
                    if not "office".startswith(arguments[0]) and not "remote".startswith(arguments[0]):
                        return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentValue(self.command_name, received_value=arguments[0], expected_value=["office", "remote"]))
                    if not "clean".startswith(arguments[2]):
                        return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentValue(self.command_name, received_value=arguments[2], expected_value="clean"))
                    count_office_minutes: bool = "office".startswith(arguments[0])
                    self._execute(date, arguments[1].minutes, CalculateType.Office if count_office_minutes else CalculateType.Remote, take_into_account_filled_dates=False)
        return CommandHandlerResult(undoable=False)

    def _execute(self, date: Date, target_minute_count: int, calculate_type: CalculateType, take_into_account_filled_dates: bool):
        date = date.fill_with_today().to_month_date()
        month: MonthData = self.data.month[date]

        total_minutes: float = 0.0
        match calculate_type:
            case CalculateType.All:
                total_minutes = month.target_minutes
                if take_into_account_filled_dates:
                    total_minutes -= sum(self.data.day[day].minutes_at_work for day in date.days_in_a_month())
            case CalculateType.Office:
                total_minutes = month.target_minutes * (1.0 - month.remote_work_ratio)
                if take_into_account_filled_dates:
                    total_minutes -= sum(self.data.day[day].minutes_at_work for day in date.days_in_a_month() if self.data.day[day].work_location == WorkLocation.OFFICE)
            case CalculateType.Remote:
                total_minutes = month.target_minutes * month.remote_work_ratio
                if take_into_account_filled_dates:
                    total_minutes -= sum(self.data.day[day].minutes_at_work for day in date.days_in_a_month() if self.data.day[day].work_location == WorkLocation.REMOTE)

        calculated_day_count: float = total_minutes / target_minute_count
        rounded_day_count: int = round(calculated_day_count)
        calculated_minute_count: float = total_minutes / rounded_day_count
        rounded_minute_count: int = round(calculated_minute_count)
        is_exact_minute_count: bool = calculated_minute_count.is_integer()
        hours: int = int(calculated_minute_count // 60)
        minutes: int = int(calculated_minute_count % 60)

        self.io.write(f"{rounded_day_count}", color=Color.Brightblue, end=" ")
        self.io.write("days each", end=" ")
        if hours == 0:
            self.io.write(f"{about_symbol if not is_exact_minute_count else ''}{rounded_minute_count} minutes", color=Color.Brightblue, end="")
        else:
            self.io.write(f"{about_symbol if not is_exact_minute_count else ''}{hours}:{minutes:02}", color=Color.Brightblue, end="")

        if calculate_type == CalculateType.Office:
            self.io.output(f" {Color.Brightcyan.value}at office{Color.Reset.value}{'.' if take_into_account_filled_dates else ' excluding already filled dates.'}")
        elif calculate_type == CalculateType.Remote:
            self.io.output(f" {Color.Brightcyan.value}remotely{Color.Reset.value}{'.' if take_into_account_filled_dates else ' excluding already filled dates.'}")
        else: # calculate_type == CalculateType.All
            self.io.output(f"{'.' if take_into_account_filled_dates else ' excluding already filled dates.'}")
