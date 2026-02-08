"""Relationship level manager."""
from __future__ import annotations


class RelationshipSystem:
    LEVELS = [
        (0, "Stranger"),
        (20, "Acquaintance"),
        (40, "Friend"),
        (60, "Close"),
        (80, "Love"),
    ]

    def get_level(self, points: int) -> str:
        level = "Stranger"
        for threshold, name in self.LEVELS:
            if points >= threshold:
                level = name
        return level
