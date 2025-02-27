from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument, AdditionalInputArgument
from work_tracker.common import Date, ReadonlyAppState
from work_tracker.config import Config
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidArgumentValue, CommandErrorInvalidDateCount
from work_tracker.text.common import wrap_text, frame_text, Color, strip_ansi


class TutorialHandler(CommandHandler):
    pages: list[str] = [
        (
            f" {Color.Brightblue.value}WorkTracker{Color.Reset.value} operates within the context of an active date, which, by default, is set to today’s date."
            f" To change the active date, simply specify a target date. The active date can be set to a particular day or an entire month."
            
            f"\n\nTo switch to a different date, enter it in the {Color.Brightblue.value}DD.MM.YYYY{Color.Reset.value} format."
            f" If you choose not to provide the complete date, the missing portions will be automatically filled in using the currently active date."
            f" This means that formats {Color.Brightblue.value}DD.{Color.Reset.value}, {Color.Brightblue.value}.MM.{Color.Reset.value},"
            f" {Color.Brightblue.value}DD.MM{Color.Reset.value}, and {Color.Brightblue.value}.MM.YYYY{Color.Reset.value} are also supported."
            f" Additionally, you can switch to month mode by entering either the full name of the month or its three-letter abbreviation."
            # f" (e.g. {Color.BRIGHT_BLUE.value}jul{Color.RESET.value} for July or {Color.BRIGHT_BLUE.value}dec{Color.RESET.value} for December)."
        ).strip(),
        (
            f"\n\nThe active date determines {Color.Brightblue.value}WorkTracker{Color.Reset.value}'s operational mode,"
            f" which can be set to {Color.Brightblue.value}today{Color.Reset.value}, {Color.Brightblue.value}day{Color.Reset.value} or {Color.Brightblue.value}month{Color.Reset.value}."
            f" Please note that certain commands may behave differently or may not be available depending on the active mode."
            
            f"\n\nEach command can also be assigned a specific date on which it should execute by placing the date before the command"
            f" (e.g. {Color.Brightblue.value}24.02 status{Color.Reset.value})."
            f" Furthermore, commands can accept multiple dates. If dates are enclosed in {Color.Brightblue.value}(){Color.Reset.value}, they will be applied to all commands in the sequence."
            
            f"\n\nCommands can be chained together using the {Color.Brightblue.value}{Config.data.input.command_chain_symbol}{Color.Reset.value} symbol, with execution proceeding from left to right."
            f" Lastly, commands can be abbreviated to the shortest unique string that distinctly identifies them."
            f" for example, the {Color.Brightblue.value}tutorial{Color.Reset.value} command can be executed simply by typing {Color.Brightblue.value}tu{Color.Reset.value}."
        ).strip(),
        (
            f" To record time spent at work for the currently active date, simply input the time in {Color.Brightblue.value}HH:MM{Color.Reset.value} format"
            f" or use descriptive terms such as {Color.Brightblue.value}50 minutes{Color.Reset.value} or {Color.Brightblue.value}2h{Color.Reset.value}."
            f" Additionally, you can add or subtract time from the current total by prefixing the time with {Color.Brightblue.value}+{Color.Reset.value} or {Color.Brightblue.value}-{Color.Reset.value}."
            
            f"\n\nTo view the total time spent working on the active date, you can use the {Color.Brightblue.value}status{Color.Reset.value} command"
            f" which will also display the target work time."
        ).strip(),
        (
            f" By default, {Color.Brightblue.value}WorkTracker{Color.Reset.value} assumes that you work full-time and have 40% remote work ratio."
            f" You can adjust the Full-Time Equivalent (FTE) for the current month by using the {Color.Brightblue.value}fte{Color.Reset.value} command."
            f" Additionally, the {Color.Brightblue.value}rwr{Color.Reset.value} command allows you to modify the required remote work ratio."
            f" Both of these commands are applicable in the month context."
            
            f"\n\nThe {Color.Brightblue.value}calendar{Color.Reset.value} command provides a calendar view with marked days, highlighting  weekends, holidays, office or remote workdays and any off-days."
            f" You can manually designate specific dates as holidays, workdays, off-days and office or remote workdays using the"
            f" {Color.Brightblue.value}holiday{Color.Reset.value}, {Color.Brightblue.value}workday{Color.Reset.value}, {Color.Brightblue.value}offday{Color.Reset.value},"
            f" {Color.Brightblue.value}office{Color.Reset.value} and {Color.Brightblue.value}remote{Color.Reset.value} commands, respectively."
            
            f"\n\nCurrently, until the {Color.Brightblue.value}setup{Color.Reset.value}, {Color.Brightblue.value}calculate{Color.Reset.value} and {Color.Brightblue.value}recalculate{Color.Reset.value}"
            f" commands are implemented, you will need to manually enter your work schedule for each month."
            f" These upcoming features will automatically generate a suggested schedule and allocate the required amount of time to be spent working each day."
        ).strip(),
        (
            f" The {Color.Brightblue.value}minutes{Color.Reset.value} and {Color.Brightblue.value}days{Color.Reset.value}"
            f" commands allow you to calculate the remaining number of days or the time left to meet your monthly work quota."
            f" {Color.Brightblue.value}WorkTracker{Color.Reset.value} also offers several additional useful commands,"
            f" such as creating macros with the {Color.Brightblue.value}macro{Color.Reset.value} command,"
            f" setting up checkpoints with the {Color.Brightblue.value}checkpoint{Color.Reset.value} command,"
            f" and adjusting {Color.Brightblue.value}WorkTracker{Color.Reset.value}'s behavior via the {Color.Brightblue.value}config{Color.Reset.value} command."
            
            f"\n\nFor detailed information about any command, please use the {Color.Brightblue.value}help{Color.Reset.value} command."
            f" If you encounter any issues, feel free to report them directly to me, and enjoy using {Color.Brightblue.value}WorkTracker{Color.Reset.value}!"
        ).strip(),
    ]
    footer_text: str = f"You can change active page by typing target page's number or by typing {Color.Brightblue.value}next{Color.Reset.value} or {Color.Brightblue.value}previous{Color.Reset.value}. To leave write {Color.Brightblue.value}quit{Color.Reset.value}."

    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 0:
            current_page_index: int = 0
            total_pages: int = len(self.pages)

            while True:
                self.display_page_(current_page_index)
                user_input: list[AdditionalInputArgument] = self.get_additional_input(custom_autocomplete=[str(number+1) for number in range(total_pages)] + ["next", "previous", "quit"])
                if len(user_input) != 1:
                    continue

                if isinstance(user_input[0], int) and 1 <= user_input[0] <= total_pages:
                    current_page_index = user_input[0]-1
                elif isinstance(user_input[0], str):
                    word: str = user_input[0].lower()
                    if "quit".startswith(word):
                        break
                    elif "next".startswith(word) and current_page_index == total_pages-1:
                        break
                    elif "next".startswith(word):
                        current_page_index += 1
                    elif "previous".startswith(word):
                        current_page_index = max(0, current_page_index-1)
                    else:
                        self.io.output("Unknown command.", color=Color.Brightred)

            return CommandHandlerResult(undoable=False)
        elif date_count == 0 and argument_count == 1:
            if arguments[0] <= 0 or arguments[0] >= len(self.pages):
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentValue(self.command_name, received_value=arguments[0], expected_value=f"page number between 1 and {len(self.pages)}"))
            self.display_page_(arguments[0]-1)
            return CommandHandlerResult(undoable=False)
        elif date_count != 0:
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDateCount(self.command_name, received_date_count=date_count, expected_date_count=0))
        else: # argument_count > 1
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))

    def display_page_(self, index: int):
        wrapped_page_text: str = wrap_text(
            text=self.pages[index],
            width=Config.data.output.max_width,
            frame_wrap=True
        )
        wrapped_footer_text: str = wrap_text(
            text=self.footer_text,
            width=Config.data.output.max_width,
            frame_wrap=True
        )

        longest_line_width: int = max([len(strip_ansi(line)) for line in wrapped_page_text.splitlines()] + [len(strip_ansi(line)) for line in wrapped_footer_text.splitlines()])

        framed_page_text: str = frame_text(
            text=wrapped_page_text,
            title="Tutorial",
            title_color=Color.Bold,
            skip_bottom_line=True,
            minimal_line_width=longest_line_width
        )
        framed_footer: str = frame_text(
            text=wrapped_footer_text,
            title=f"page {index+1}/{len(self.pages)}",
            footer_title=True,
            extend_top_line=True,
            minimal_line_width=longest_line_width
        )

        self.io.write(framed_page_text)
        self.io.output(framed_footer)