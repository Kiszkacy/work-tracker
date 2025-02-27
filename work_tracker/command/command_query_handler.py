import importlib
import inspect

from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.command_history import CommandHistory
from work_tracker.command.command_manager import CommandManager
from work_tracker.command.common import CommandQuery
from work_tracker.command.common import KeyManager
from work_tracker.common import AppData, Date, AppState, Mode, ReadonlyAppState
from work_tracker.config import Config
from work_tracker.text.common import Color
from work_tracker.text.input_output_handler import InputOutputHandler


class CommandQueryHandler:
    def __init__(self, data: AppData, io: InputOutputHandler, state: AppState):
        self.data: AppData = data
        self.io: InputOutputHandler = io
        self.state: AppState = state

        self._history: CommandHistory = CommandHistory(max_size=Config.data.command.undo_history_size)
        self._history.add(KeyManager.encode(self.data), 'initial state')

        self._handlers: dict[str, CommandHandler] = {}
        self.initialize_handlers()

        self._during_execute_after: bool = False

    def initialize_handlers(self):
        for command in [CommandManager.time_command, CommandManager.date_command, CommandManager.macro_execute_command] + CommandManager.commands:
            module_name: str = f"work_tracker.command.commands.{command.snake_case_name}" # TODO hardcoded path might break easily
            class_name: str = f"{command.camel_case_name}Handler"

            try:
                module = importlib.import_module(module_name)
                handler_class: type = getattr(module, class_name)

                if inspect.isclass(handler_class):
                    self._handlers[command.name] = handler_class(self.data, self.io)
                else:
                    raise TypeError(
                        f"Failed to initialize handler for command '{command.name}'. "
                        f"{class_name} is not a class."
                    )
            except (ModuleNotFoundError, AttributeError) as e:
                raise ImportError(
                    f"Failed to initialize handler for command '{command.name}'. "
                    f"Ensure the handler class '{class_name}' exists in the module '{module_name}'."
                ) from e

    def run(self, query: CommandQuery):
        result: CommandHandlerResult = self._handlers[query.command.name].handle(query.dates, query.date_count, query.arguments, query.argument_count, self._readonly_app_state())

        if result.execute_after is not None:
            self._during_execute_after = True
            for query in result.execute_after:
                self.run(query)
            self._during_execute_after = False

        if result.undoable and not self._during_execute_after:
            self._history.add(KeyManager.encode(self.data), query.raw_text)
        if result.error is not None:
            self.io.output(f"ERROR: {result.error.message or 'missing error description'}", color=Color.Brightred)
        if result.change_active_date is not None:
            self.state.active_date = result.change_active_date
            if self.state.active_date == Date.today():
                self.state.mode = Mode.Today
            elif self.state.active_date.is_day_date():
                self.state.mode = Mode.Day
            elif self.state.active_date.is_month_date():
                self.state.mode = Mode.Month
            else: # default to today mode if no matching date format was found
                self.state.mode = Mode.Today
        if result.change_state_by is not None:
            self._change_state_by(result.change_state_by)

    def _readonly_app_state(self) -> ReadonlyAppState:
        return ReadonlyAppState(
            active_date=self.state.active_date,
            mode=self.state.mode,
            states=self._history.states,
            current_state_index=self._history.current_state_index
        )

    def _change_state_by(self, offset: int):
        state_key: str | None = None
        for _ in range(abs(offset)):
            state_key = self._history.undo() if offset < 0 else self._history.redo()

        if state_key is None:
            raise Exception() # TODO
        else:
            self.data.copy_from(KeyManager.decode(state_key))
