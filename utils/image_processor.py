"""Image processing utility."""
from PIL import Image, ImageOps


def resize_image(source: str, output: str, width: int, height: int) -> None:
    img = Image.open(source)
    ImageOps.fit(img, (width, height)).save(output)
