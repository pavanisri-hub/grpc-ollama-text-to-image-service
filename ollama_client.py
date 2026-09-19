from __future__ import annotations

from typing import Any

import requests

from config import (
    OLLAMA_GENERATE_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT_SECONDS,
)


class OllamaUnavailableError(Exception):
    """Raised when the local Ollama server cannot be reached."""


class OllamaResponseError(Exception):
    """Raised when Ollama returns an unsuccessful HTTP response."""


def generate_image(prompt: str) -> dict[str, Any]:
    """Send a non-streaming generation request to the configured Ollama API."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "images": [],
    }

    try:
        response = requests.post(
            OLLAMA_GENERATE_URL,
            json=payload,
            timeout=OLLAMA_TIMEOUT_SECONDS,
        )
    except requests.exceptions.ConnectionError as error:
        raise OllamaUnavailableError("Ollama service is not available.") from error
    except requests.exceptions.Timeout as error:
        raise OllamaUnavailableError("Ollama service is not available.") from error
    except requests.exceptions.RequestException as error:
        raise OllamaResponseError("Ollama service returned an error.") from error

    if not response.ok:
        raise OllamaResponseError("Ollama service returned an error.")

    try:
        return response.json()
    except ValueError as error:
        raise OllamaResponseError("Ollama service returned an invalid JSON response.") from error