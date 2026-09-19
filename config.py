from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

GRPC_HOST = os.getenv("GRPC_HOST", "[::]")
GRPC_PORT = int(os.getenv("GRPC_PORT", "50051"))

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_GENERATE_URL = f"{OLLAMA_BASE_URL.rstrip('/')}/api/generate"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llava")
OLLAMA_TIMEOUT_SECONDS = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))

OUTPUT_DIRECTORY = PROJECT_ROOT / os.getenv("OUTPUT_DIRECTORY", "output")
MAX_PROMPT_LENGTH = int(os.getenv("MAX_PROMPT_LENGTH", "512"))