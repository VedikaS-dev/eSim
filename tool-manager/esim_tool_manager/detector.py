from __future__ import annotations

import shutil
import subprocess
from dataclasses import asdict
from typing import Sequence

from .models import ToolSpec, ToolStatus
from .platform_support import detect_package_manager
from .versioning import extract_version, policy_message, satisfies


def run_command(
    command: Sequence[str],
    timeout: int = 30,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def query_installed(spec: ToolSpec, package_manager: str | None = None) -> ToolStatus:
    executable = shutil.which(spec.executable)
    pm = package_manager or detect_package_manager()
    if not executable:
        return ToolStatus(spec.name, False, None, None, False, pm, False, "Executable not found on PATH")
    try:
        result = run_command([executable, *spec.version_args], timeout=15)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return ToolStatus(spec.name, True, None, executable, False, pm, False, f"Version probe failed: {exc}")

    text = "\n".join(filter(None, (result.stdout, result.stderr))).strip()
    version = extract_version(text)
    if not version:
        message = "Installed, but version could not be parsed"
        return ToolStatus(spec.name, True, None, executable, False, pm, False, message)

    meets = satisfies(version, spec)
    message = "OK" if meets else policy_message(spec)
    return ToolStatus(spec.name, True, version, executable, meets, pm, meets, message)


def status_dict(status: ToolStatus) -> dict:
    return asdict(status)
