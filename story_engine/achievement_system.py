"""Achievement tracker and evaluator."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class AchievementSystem:
    def __init__(self, source: Path):
        with source.open("r", encoding="utf-8") as f:
            self.achievements: dict[str, dict[str, Any]] = json.load(f)

    def list_all(self) -> dict[str, dict[str, Any]]:
        return self.achievements

    def evaluate(self, state: dict[str, Any]) -> list[str]:
        unlocked: list[str] = []
        stats = state.get("stats", {})
        for key, data in self.achievements.items():
            rule = data.get("rule", {})
            stat_name = rule.get("stat")
            minimum = int(rule.get("min", 0))
            if stat_name and int(stats.get(stat_name, 0)) >= minimum:
                unlocked.append(key)
        return unlocked
