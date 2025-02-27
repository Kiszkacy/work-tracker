from dataclasses import dataclass


@dataclass(frozen=True)
class CommandHistoryEntry:
    state_key: str
    command: str


class CommandHistory:
    def __init__(self, max_size: int):
        self._max_size: int = max_size
        self._current_state_index: int = -1
        self._states: list[CommandHistoryEntry] = []

    def add(self, state_key: str, command_used: str):
        if self._current_state_index < self._max_size:
            self._states = self._states[:self._current_state_index + 1]

        if self._current_state_index == self._max_size:
            self._states.pop(0)
        else:
            self._current_state_index += 1

        self._states.append(CommandHistoryEntry(
            state_key=state_key,
            command=command_used
        ))

    def undo(self) -> str | None:
        if self._current_state_index > 0:
            self._current_state_index -= 1
            return self._states[self._current_state_index].state_key
        return None

    def redo(self) -> str | None:
        if self._current_state_index < len(self._states) - 1:
            self._current_state_index += 1
            return self._states[self._current_state_index].state_key
        return None

    @property
    def states(self) -> tuple[CommandHistoryEntry]:
        return tuple(self._states)

    @property
    def current_state_index(self) -> int:
        return self._current_state_index
