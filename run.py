from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"
SERVER_FILE = PROJECT_ROOT / "server.py"


def run_command(command: list[str]) -> None:
    """Run a command and stop immediately if it fails."""
    subprocess.run(command, check=True, cwd=PROJECT_ROOT)


def main() -> None:
    """Install dependencies and start the gRPC server."""
    run_command(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "-r",
            str(REQUIREMENTS_FILE),
        ]
    )
    run_command([sys.executable, str(SERVER_FILE)])


if __name__ == "__main__":
    main()