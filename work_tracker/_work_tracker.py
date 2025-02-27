import calendar
import datetime
import shutil
import signal
import subprocess
import sys
import traceback
from pathlib import Path

from workalendar.registry import registry

from work_tracker import __version__
from work_tracker.checkpoint_manager import CheckpointManager
from work_tracker.command.command_parser import CommandParser
from work_tracker.command.command_query_handler import CommandQueryHandler
from work_tracker.command.common import ParseResult
from work_tracker.common import AppData, Date, Mode, AppState, get_data_path
from work_tracker.text.common import Color
from work_tracker.text.input_output_handler import InputOutputHandler
from .config import Config
from .error import VersionCheckError


class WorkTracker:
    def __init__(self):
        self.state: AppState = AppState()
        self.data: AppData
        self.io: InputOutputHandler
        self.command_handler: CommandQueryHandler
        self._initialized: bool = False

    def initialize(self, check_is_new_version_available: bool = True):
        self._initialized = True

        if is_first_time_launch := self._is_first_time_launch():
            self._create_basic_files()
        if was_version_file_missing := self._is_version_file_missing():
            self._update_version_file()
        if was_config_file_missing := self._is_config_file_missing():
            self._create_default_config_file()
        if was_macros_file_missing := self._is_macros_file_missing():
            self._create_default_macros_file()
        if was_updated_since_last_launch := self._was_updated_since_last_launch():
            self._update_version_file()

        # config access check must be before io, because io uses config values
        if not Config.ready():
            raise RuntimeError("Something went wrong trying to access config.")

        self._initialize_io()
        if is_first_time_launch:
            self._first_time_prompt()
        else:
            if was_version_file_missing:
                self.io.output("WARNING: version file could not be found. This may lead to unpredicted behavior.", color=Color.Yellow)
            if was_config_file_missing:
                self.io.output("WARNING: config file could not be found. Default config will be used instead.", color=Color.Yellow)
            if was_macros_file_missing:
                self.io.output("WARNING: macros file could not be found. Default macros will be used instead.", color=Color.Yellow)

        if not is_first_time_launch:
            self._load_data()
            if self.data is None:
                self.io.output("WARNING: it appears that no saved data file was found to load from. As a result, the app will default to the first-time launch screen.", color=Color.Yellow)
                self._first_time_prompt()
            elif not self.data.is_latest_data_version():
                self.data.update_data_to_latest_version()

        self._initialize_command_handler()
        self._clear_old_cache()

        if not was_updated_since_last_launch and check_is_new_version_available and (latest_version := self._is_new_version_available()) is not None:
            self._display_new_version_available_message(latest_version)
        self.io.output(f"Using {Color.Brightblue.value}WorkTracker{Color.Clear.value} version {Color.Brightblue.value}{__version__}{Color.Clear.value}.")

    def _is_first_time_launch(self) -> bool:
        expected_files: list[Path] = [get_data_path().joinpath("version"), get_data_path().joinpath("config.yaml"), get_data_path().joinpath("macros.txt")]
        return all(not path.exists() for path in expected_files)

    def _create_basic_files(self):
        self._create_default_config_file()
        self._create_default_macros_file()

    def _create_default_config_file(self):
        shutil.copy(Path(__file__).parent.joinpath("data/default.config.yaml"), get_data_path().joinpath("config.yaml"))

    def _create_default_macros_file(self):
        shutil.copy(Path(__file__).parent.joinpath("data/default.macros.txt"), get_data_path().joinpath("macros.txt"))

    def _initialize_io(self):
        self.io = InputOutputHandler()

    def _load_data(self):
        self.data = CheckpointManager.load_latest()

    def _first_time_prompt(self):
        self.io.write("Welcome to WorkTracker!", color=Color.Brightblue)
        self.io.write("WorkTracker helps you track your work hours efficiently and manage your schedule with ease.", color=Color.Cyan)
        self.io.output(f"Before you start using it, please provide your country code. This will allow {Color.Brightblue.value}WorkTracker{Color.Reset.value} to automatically import all relevant holidays and mark your non-working days accordingly.")

        country_code: str
        valid_codes: list[str] = sorted(list(registry.get_calendars().keys()))
        while True:
            country_code = self.io.input(f"{Config.data.input.prefix} ", custom_autocomplete=valid_codes).upper()
            if country_code in valid_codes: # TODO use of private method
                break
            else:
                self.io.output("Invalid country code. Please input valid contry code.", color=Color.Brightred)

        self.io.output("Would you like to run the initial setup? This process can take some time but is recommended, as it enables the app to automatically fill your calendar with the suggested work schedule.")
        user_input: str = self.io.input(f"{Config.data.input.prefix} ", custom_autocomplete=["yes", "no"])
        if "yes".startswith(user_input):
            self.io.output("Setup command is not yet implemented. Skipping setup phase...", color=Color.Brightred)
        else:
            self.io.output(f"Initial setup skipped. You can always run setup later by using {Color.Brightblue.value}setup{Color.Reset.value} command.")

        self.data = AppData(country_code=country_code)
        CheckpointManager.save("initial", self.data)

        self.io.write(f"Everything is set up and ready.", color=Color.Cyan, end=" ")
        self.io.write(f"To view a list of available commands type {Color.Brightblue.value}help{Color.Reset.value}.", end=" ")
        self.io.write(f"For detailed information about a specific command use {Color.Brightblue.value}help <command_name>{Color.Reset.value}.", end=" ")
        self.io.write(f"It is recommended that you use {Color.Brightblue.value}tutorial{Color.Reset.value} command to quickly get familiar with the available features.", end=" ")
        self.io.output(f"Remember to leave {Color.Brightblue.value}WorkTracker{Color.Reset.value} by using {Color.Brightblue.value}exit{Color.Reset.value} command to avoid {Color.Underline.value}{Color.Brightred.value}loss of data{Color.Reset.value}!")

    def _is_version_file_missing(self) -> bool:
        return not get_data_path().joinpath("version").exists() # TODO make file name a constant

    def _is_config_file_missing(self) -> bool:
        return not get_data_path().joinpath("config.yaml").exists() # TODO make file name a constant

    def _is_macros_file_missing(self) -> bool:
        return not get_data_path().joinpath("macros.txt").exists() # TODO make file name a constant

    def _was_updated_since_last_launch(self) -> bool:
        path: Path = get_data_path().joinpath("version")
        if not path.exists():
            raise RuntimeError("Something went wrong when trying to access version file.")

        with open(path, "r") as file:
            version: str = file.read()

        return version < __version__

    def _update_version_file(self):
        with open(get_data_path().joinpath("version"), "w") as file:
            file.write(__version__)

    def _initialize_command_handler(self):
        self.command_handler = CommandQueryHandler(self.data, self.io, self.state)

    def _is_new_version_available(self) -> str | None:
        try:
            installed_version: str = __version__
            result = subprocess.run(
                ["pip", "index", "versions", "work-tracker"],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                self.io.output("WARNING: unable to retrieve data from pip while checking for available updates.", color=Color.Yellow)
                return None

            latest_version: str = result.stdout.strip().split("\n")[-1].split()[-1]
            return latest_version if installed_version != latest_version else None
        except subprocess.SubprocessError as e:
            raise VersionCheckError("Subprocess error during version check.")
        except Exception as e:
            raise VersionCheckError(f"Unexpected error: {e}")

    def _display_new_version_available_message(self, version: str):
        self.io.write(f"New version {Color.Brightcyan.value}{version}{Color.Reset.value} is available!", end=" ")
        self.io.output(f"Update with {Color.Brightblue.value}pip install --upgrade work-tracker{Color.Reset.value}.")

    def _clear_old_cache(self):
        CheckpointManager.clear_cache()

    def _at_crash_exit(self, crash_message: str | None = None, exception: Exception | None = None):
        CheckpointManager.save(f"crash-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}", self.data)
        with open(get_data_path().joinpath(f"crash-log-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"), "w") as file:
            if crash_message is not None:
                file.write(crash_message)
            if exception is not None:
                traceback.print_exc(file=file)
        sys.exit()

    def _at_exit(self):
        CheckpointManager.save(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}", self.data)
        sys.exit()

    def handle_exit_signal(self): # TODO check if this works | no it doesnt :(
        self._at_crash_exit(crash_message=f"received exit signal")

    def _run(self):
        error_log_last_processed_input: str = "None"
        try:
            while True:
                today: Date = Date.today()
                mode: Mode = self.state.mode
                date: Date = self.state.active_date
                prefix: str = (
                    f"{Config.data.input.prefix} "                                            if mode == Mode.Today else
                    f"[{date.day:02}.{date.month:02}.{date.year}]{Config.data.input.prefix} " if mode == Mode.Day and today.year != date.year else
                    f"[{date.day:02}.{date.month:02}]{Config.data.input.prefix} "             if mode == Mode.Day and today.year == date.year else
                    f"[{calendar.month_abbr[date.month].lower()}]{Config.data.input.prefix} " if mode == Mode.Month else
                    "?> "
                )

                user_input: str = self.get_user_input(prefix)
                error_log_last_processed_input = user_input

                result: ParseResult = CommandParser.parse(user_input)
                if result.error:
                    self.io.output(f"ERROR: {result.error.message or 'missing error description'}", color=Color.Brightred)
                    continue

                for query in result.queries:
                    self.command_handler.run(query)
        except KeyboardInterrupt:
            self.io.output("UNSAFE EXIT: saving data...", color=Color.Brightred, end="")
            self._at_exit()
        except Exception as exception:
            self.io.output("FATAL ERROR: saving data and creating error log...", color=Color.Brightred, end="")
            self._at_crash_exit(crash_message=f"{error_log_last_processed_input}\n\n", exception=exception)

    def start(self):
        if not self._initialized:
            self.initialize()

        # TODO add atexit.register() to automatically save data somewhere here ?
        signal.signal(signal.SIGINT, self.handle_exit_signal)
        signal.signal(signal.SIGTERM, self.handle_exit_signal)

        self._run()

    def get_user_input(self, prefix: str) -> str:
        return self.io.input(prefix)
