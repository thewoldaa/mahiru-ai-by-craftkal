"""Save and load state utility."""
from __future__ import annotations

import json
from typing import Any


class SaveManager:
    def pack_state(self, state: dict[str, Any]) -> str:
        return json.dumps(state, ensure_ascii=False)

    def unpack_state(self, payload: str) -> dict[str, Any]:
        if not payload:
            return {}
        return json.loads(payload)
