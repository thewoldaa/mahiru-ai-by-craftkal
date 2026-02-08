"""Simple deploy checker."""
import json
from pathlib import Path

config = json.loads(Path("config.json").read_text(encoding="utf-8"))
print(f"Deploy check: {config['project_name']} v{config['version']}")
print("Gunakan Dockerfile atau python app.py untuk deploy.")
