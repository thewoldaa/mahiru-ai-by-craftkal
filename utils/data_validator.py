"""JSON data validation helpers."""
from typing import Any


def validate_scene(scene: dict[str, Any]) -> bool:
    required = ["id", "chapter", "dialogue", "choices"]
    return all(key in scene for key in required)
