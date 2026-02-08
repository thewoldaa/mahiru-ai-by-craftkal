"""Simple in-memory flag manager."""
from __future__ import annotations


class FlagManager:
    def __init__(self) -> None:
        self.flags: dict[str, bool] = {}

    def set(self, key: str, value: bool = True) -> None:
        self.flags[key] = value

    def get(self, key: str, default: bool = False) -> bool:
        return self.flags.get(key, default)
