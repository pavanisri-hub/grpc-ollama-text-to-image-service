from __future__ import annotations

import base64
import binascii
import re
from pathlib import Path
from typing import Any

from config import OUTPUT_DIRECTORY


class ImageStorageError(Exception):
    """Raised when image data cannot be safely saved as a PNG file."""


def ensure_output_directory() -> None:
    """Create the output directory when it does not already exist."""
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)


def build_image_path(request_id: str) -> Path:
    """Create a safe, deterministic PNG path inside the output directory."""
    safe_request_id = re.sub(r"[^A-Za-z0-9_-]", "_", request_id.strip())

    if not safe_request_id:
        safe_request_id = "generated-image"

    return OUTPUT_DIRECTORY / f"{safe_request_id}.png"


def save_base64_png(image_base64: str, request_id: str) -> str:
    """Decode base64 image content, validate its PNG signature, and save it."""
    if not isinstance(image_base64, str) or not image_base64.strip():
        raise ImageStorageError("Ollama response did not contain image data.")

    try:
        image_bytes = base64.b64decode(image_base64, validate=True)
    except (binascii.Error, ValueError) as error:
        raise ImageStorageError("Ollama returned invalid image data.") from error

    png_signature = b"\x89PNG\r\n\x1a\n"
    if not image_bytes.startswith(png_signature):
        raise ImageStorageError("Ollama response did not contain a valid PNG image.")

    ensure_output_directory()
    image_path = build_image_path(request_id)

    try:
        image_path.write_bytes(image_bytes)
    except OSError as error:
        raise ImageStorageError("Failed to save the generated image.") from error

    return image_path.relative_to(Path.cwd()).as_posix()


def extract_first_image(response_data: dict[str, Any]) -> str:
    """Extract the first base64 image string from an Ollama response."""
    images = response_data.get("images")

    if not isinstance(images, list) or not images:
        raise ImageStorageError("Ollama response did not contain image data.")

    image_base64 = images[0]
    if not isinstance(image_base64, str):
        raise ImageStorageError("Ollama response did not contain image data.")

    return image_base64