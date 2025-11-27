"""Media storage service for images."""
import os
from pathlib import Path
from typing import Optional

MEDIA_DIR = Path("media")
MEDIA_DIR.mkdir(exist_ok=True)


def save_image(mcq_id: int, image_bytes: bytes, extension: str = "png") -> str:
    """Save image bytes to media folder and return relative path."""
    filename = f"mcq_{mcq_id}.{extension}"
    filepath = MEDIA_DIR / filename
    with open(filepath, "wb") as f:
        f.write(image_bytes)
    return str(filepath)


def get_image_path(mcq_id: int, extension: str = "png") -> Optional[Path]:
    """Get image path if it exists."""
    filename = f"mcq_{mcq_id}.{extension}"
    filepath = MEDIA_DIR / filename
    return filepath if filepath.exists() else None


def load_image_bytes(mcq_id: int, extension: str = "png") -> Optional[bytes]:
    """Load image bytes if file exists."""
    filepath = get_image_path(mcq_id, extension)
    if not filepath:
        return None
    with open(filepath, "rb") as f:
        return f.read()


def delete_image(mcq_id: int, extension: str = "png") -> bool:
    """Delete image file if it exists."""
    filepath = get_image_path(mcq_id, extension)
    if filepath:
        filepath.unlink()
        return True
    return False

