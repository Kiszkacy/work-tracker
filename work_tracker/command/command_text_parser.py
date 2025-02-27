import re


class CommandTextParser:
    def __init__(self, text: str):
        self._active_word_index: int = -1
        self._words: list[str] = self._split_words(text)
        self._checkpoint_queue: list[int] = []

    @staticmethod
    def _split_words(text: str) -> list[str]:
        pattern: str = r'"([^"]+)"|\'([^\']+)\'|(\S+)' # this pattern splits at whitespaces unless string is inside quotes
        matches: list = re.findall(pattern, text)
        return [match[0] or match[1] or match[2] for match in matches]

    def next(self, times: int = 1) -> str | None:
        self._active_word_index = min(self._active_word_index + times, len(self._words))
        if self._active_word_index == len(self._words):
            return None
        return self._words[self._active_word_index]

    def peak(self) -> str | None:
        if self._active_word_index + 1 >= len(self._words):
            return None
        return self._words[self._active_word_index + 1]

    def previous(self, times: int = 1) -> str | None:
        self._active_word_index = max(self._active_word_index - times, -1)
        if self._active_word_index == -1:
            return None
        return self._words[self._active_word_index]

    def checkpoint(self):
        self._checkpoint_queue.append(self._active_word_index)

    def go_to_checkpoint(self):
        if len(self._checkpoint_queue) == 0:
            raise RuntimeError("No checkpoints available to revert to.")
        self._active_word_index = self._checkpoint_queue.pop()

    def character_position(self) -> int:
        return sum([len(word)+1 for word in self._words[:self._active_word_index]])-1
