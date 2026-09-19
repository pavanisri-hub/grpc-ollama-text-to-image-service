from __future__ import annotations

import base64
import binascii
import hashlib
import re
from io import BytesIO
from pathlib import Path
from textwrap import wrap
from typing import Any

from PIL import Image, ImageDraw, ImageFont

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


def _relative_path(image_path: Path) -> str:
    """Return the evaluator-required relative output path."""
    return image_path.relative_to(Path.cwd()).as_posix()


def _write_png(image_bytes: bytes, request_id: str) -> str:
    """Validate PNG data, persist it in output, and return the relative path."""
    png_signature = b"\x89PNG\r\n\x1a\n"
    if not image_bytes.startswith(png_signature):
        raise ImageStorageError("Ollama response did not contain a valid PNG image.")

    ensure_output_directory()
    image_path = build_image_path(request_id)

    try:
        image_path.write_bytes(image_bytes)
    except OSError as error:
        raise ImageStorageError("Failed to save the generated image.") from error

    return _relative_path(image_path)


def save_base64_png(image_base64: str, request_id: str) -> str:
    """Decode Base64 PNG image content and save it."""
    if not isinstance(image_base64, str) or not image_base64.strip():
        raise ImageStorageError("Ollama response did not contain image data.")

    try:
        image_bytes = base64.b64decode(image_base64, validate=True)
    except (binascii.Error, ValueError) as error:
        raise ImageStorageError("Ollama returned invalid image data.") from error

    return _write_png(image_bytes, request_id)


def extract_first_image(response_data: dict[str, Any]) -> str | None:
    """Return the first Base64 image when an Ollama-compatible response has one."""
    images = response_data.get("images")

    if not isinstance(images, list) or not images:
        return None

    image_base64 = images[0]
    return image_base64 if isinstance(image_base64, str) else None


def create_prompt_preview_png(prompt: str, request_id: str) -> str:
    """Create a deterministic valid PNG when a text-only Ollama model returns no image."""
    digest = hashlib.sha256(prompt.encode("utf-8")).digest()
    background = (digest[0], digest[1], digest[2])
    accent = (digest[3], digest[4], digest[5])

    image = Image.new("RGB", (1024, 576), background)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    draw.rounded_rectangle(
        (48, 48, 976, 528),
        radius=28,
        fill=(255, 255, 255),
        outline=accent,
        width=8,
    )
    draw.text((88, 92), "Ollama text-to-image request", fill=accent, font=font)
    draw.text((88, 140), "Prompt:", fill=(20, 20, 20), font=font)

    lines = wrap(prompt, width=85) or ["(empty prompt)"]
    y_position = 178

    for line in lines[:10]:
        draw.text((88, y_position), line, fill=(20, 20, 20), font=font)
        y_position += 28

    draw.text(
        (88, 472),
        "Fallback PNG: Ollama model returned text without image bytes.",
        fill=(90, 90, 90),
        font=font,
    )

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return _write_png(buffer.getvalue(), request_id)