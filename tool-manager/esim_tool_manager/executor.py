from __future__ import annotations

from typing import Sequence

from .audit import log_event
from .detector import run_command


def execute(command: Sequence[str], *, dry_run: bool = True, timeout: int = 900) -> int:
    command = list(command)
    log_event("command", {"command": command, "dry_run": dry_run})
    if dry_run:
        return 0
    try:
        result = run_command(command, timeout=timeout)
    except Exception as exc:
        log_event("command_error", {"command": command, "error": str(exc)})
        return 1

    log_event(
        "command_result",
        {
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout[-4000:],
            "stderr": result.stderr[-4000:],
        },
    )
    return result.returncode
