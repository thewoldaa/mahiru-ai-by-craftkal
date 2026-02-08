"""Inventory and item enrichment manager."""
from __future__ import annotations

import json
from pathlib import Path


class InventorySystem:
    def __init__(self, item_file: Path):
        with item_file.open("r", encoding="utf-8") as f:
            self.items = json.load(f)

    def enrich_inventory(self, entries: list[dict[str, int]]):
        payload = []
        for entry in entries:
            item_data = self.items.get(entry["item_id"], {})
            payload.append({**entry, **item_data})
        return payload
