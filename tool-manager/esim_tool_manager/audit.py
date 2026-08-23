from __future__ import annotations

import json
import time
from pathlib import Path


def default_state_dir() -> Path:
    return Path.home() / ".esim-tool-manager"


def audit_log_path() -> Path:
    return default_state_dir() / "manager.jsonl"


def log_event(event: str, payload: dict) -> None:
    path = audit_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "event": event, **payload}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
