"""Generate placeholder assets for development."""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


def create_placeholder(path: Path, text: str, size=(1280, 720)):
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", size, color=(30, 30, 80))
    draw = ImageDraw.Draw(image)
    draw.text((20, 20), text, fill=(255, 255, 255))
    image.save(path)


if __name__ == "__main__":
    for chapter in range(1, 11):
        for scene in range(1, 11):
            create_placeholder(ROOT / "static/images/backgrounds" / f"chapter_{chapter}_bg_{scene}.png", f"Chapter {chapter} Scene {scene}")
