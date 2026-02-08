"""Story loader and parser for chapter scene JSON files."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class StoryLoader:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.chapter_path = base_path / "chapters"
        self.characters = self._load_json(base_path / "characters" / "characters.json")
        self.endings = self._load_json(base_path / "endings" / "endings.json")
        self._scene_cache = self._build_scene_index()

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _build_scene_index(self) -> dict[str, dict[str, Any]]:
        scene_index: dict[str, dict[str, Any]] = {}
        for chapter_file in sorted(self.chapter_path.glob("chapter_*.json")):
            chapter_data = self._load_json(chapter_file)
            for scene in chapter_data.get("scenes", []):
                scene_index[scene["id"]] = scene
        return scene_index

    def get_scene(self, scene_id: str) -> dict[str, Any] | None:
        return self._scene_cache.get(scene_id)

    def process_choice(self, scene_id: str, choice_id: str, state: dict[str, Any]) -> dict[str, Any]:
        scene = self.get_scene(scene_id)
        if not scene:
            return {"error": "Scene tidak ditemukan"}

        choices = {choice["id"]: choice for choice in scene.get("choices", [])}
        choice = choices.get(choice_id)
        if not choice:
            return {"error": "Choice tidak valid"}

        stats = state.setdefault("stats", {})
        flags = state.setdefault("flags", {})
        for key, val in choice.get("stat_changes", {}).items():
            stats[key] = int(stats.get(key, 0)) + int(val)

        flags.update(scene.get("set_flags", {}))

        return {
            "next_scene": choice.get("next_scene"),
            "state": state,
            "chapter": scene.get("chapter", 1),
        }

    def get_gallery_data(self) -> dict[str, Any]:
        return {
            "cg": [
                {"id": "cg_01", "title": "Pertemuan Pertama", "unlocked": True},
                {"id": "cg_02", "title": "Festival Malam", "unlocked": False},
            ]
        }
