from typing import Any


class Clipboard:
    _data: dict[str, Any] = {}
    COPY_PASTE_KEY: str = "@copy-paste"

    @classmethod
    def set(cls, key: str, value: Any):
        cls._data[key] = value

    @classmethod
    def get(cls, key: str) -> Any | None:
        return cls._data.get(key)

    @classmethod
    def has(cls, key: str) -> bool:
        return key in cls._data

    @classmethod
    def clear(cls):
        cls._data.clear()

    @classmethod
    def pop(cls, key: str) -> Any | None:
        try:
            return cls._data.pop(key, None)
        except KeyError:
            return None
