import re

from work_tracker.command.common import Command, CommandTemplate


class CommandInitializer:
    _shortest_command_string: dict[str, str] = {} # key: value -> shortest_command_string: command_name

    @classmethod
    def reset(cls):
        cls._shortest_command_string.clear()

    @classmethod
    def initialize_commands(cls, commands: list[CommandTemplate]) -> list[Command]:
        cls.reset()

        commands_dict: dict[str, CommandTemplate] = {command.name: command for command in commands}
        if len(commands_dict.keys()) != len(commands):
            raise RuntimeError(f"Could not initialize commands, there are duplicated command names.")

        cls._find_not_conflicting_shortest_command_string_for(commands)

        return [
            Command(
                name=command_name,
                help=commands_dict[command_name].help,
                abbreviations=commands_dict[command_name].abbreviations,
                shortest_valid_string=shortest_string,
                snake_case_name=re.sub(r'[-. ]', '_', command_name),
                camel_case_name="".join(word.capitalize() for word in re.sub(r'[-. ]', '_', command_name).split('_')),
                valid_argument_types=sorted(commands_dict[command_name].valid_argument_types, key=len),
                supported_modes=commands_dict[command_name].supported_modes,
            ) for shortest_string, command_name in sorted(cls._shortest_command_string.items())
        ]

    @classmethod
    def _find_not_conflicting_shortest_command_string_for(cls, commands: list[CommandTemplate]):
        target_string_length: int = 1
        abbreviations: set[str] = cls._get_abbreviations(commands)

        commands_left: list[str] = [command.name for command in commands]
        while len(commands_left) != 0:
            commands_left = cls._find_not_conflicting_command_string_of_length_for(commands_left, abbreviations, target_string_length)
            target_string_length += 1

    @classmethod
    def _get_abbreviations(cls, commands: list[CommandTemplate]) -> set[str]:
        abbreviations: set[str] = set()
        for command in commands:
            for abbreviation in command.abbreviations:
                if abbreviation in abbreviations:
                    raise RuntimeError(f"Could not initialize commands, found duplicated command abbreviation: '{abbreviation}'.")
                abbreviations.add(abbreviation)
        return abbreviations

    @classmethod
    def _find_not_conflicting_command_string_of_length_for(cls, commands: list[str], abbreviations: set[str], target_string_length: int) -> list[str]: # TODO check if this can be simplified
        remaining_commands: set[str] = set()
        substrings_to_pop: set[str] = set()

        for command in commands:
            command_substring: str = command[:target_string_length]
            substring_is_full_command_name: bool = len(command_substring) == len(command)
            substring_is_an_abbreviation: bool = command_substring in abbreviations
            substring_already_exists: bool = command_substring in cls._shortest_command_string.keys()
            found_substring_is_full_command_name: bool = command_substring == cls._shortest_command_string.get(command_substring)

            if substring_is_an_abbreviation and substring_is_full_command_name:
                raise RuntimeError(f"Command '{command}' could not be shorten and is equal to one of the special abbreviations of another command.")
            elif substring_is_an_abbreviation:
                remaining_commands.add(command)
            elif substring_already_exists and substring_is_full_command_name:
                remaining_commands.add(cls._shortest_command_string[command_substring])
                substrings_to_pop.add(command_substring)
                cls._shortest_command_string[command_substring] = command
            elif substring_already_exists and not found_substring_is_full_command_name:
                remaining_commands.add(cls._shortest_command_string[command_substring])
                remaining_commands.add(command)
                substrings_to_pop.add(command_substring)
            elif not substring_already_exists or substring_is_full_command_name:
                cls._shortest_command_string[command_substring] = command
            else:
                remaining_commands.add(command)

        for substring in substrings_to_pop:
            cls._shortest_command_string.pop(substring)

        return list(remaining_commands)
