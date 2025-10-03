import os
from typing import Any
from dotenv import load_dotenv
from PIL import Image
import io
import base64
import mimetypes

load_dotenv()


def get_env(key: str) -> Any:
    value = os.getenv(key)

    if value is None:
        raise ValueError(f"Environment variable {key} not found.")
    return value


def compress_image(
    image_data: bytes, max_size_kb: int = 800
) -> tuple[str, str]:
    """Compress image and return (compressed_base64, format)"""
    img = Image.open(io.BytesIO(image_data))

    # Detect original format
    original_format = img.format  # 'JPEG', 'PNG', etc.

    # Convert RGBA to RGB if needed (for JPEG compatibility)
    if img.mode in ("RGBA", "LA", "P"):
        rgb_img = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        rgb_img.paste(
            img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None
        )
        img = rgb_img

    # Resize if needed
    max_width, max_height = 1200, 1600
    if img.width > max_width or img.height > max_height:
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

    # Compress - use JPEG for efficiency
    quality = 92
    while quality > 30:
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        size_kb = buffer.tell() / 1024

        if size_kb <= max_size_kb:
            break
        quality -= 5

    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8"), original_format


def encode_base64(data: bytes, filename: str):
    """Encode file as base64 and detect MIME type."""
    mime_type, _ = mimetypes.guess_type(filename)
    if not mime_type:
        mime_type = "application/octet-stream"

    b64_str = base64.b64encode(data).decode("utf-8")
    return {
        "file": b64_str,
        "type": mime_type,
        "name": filename,
    }
