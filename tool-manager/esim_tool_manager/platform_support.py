from __future__ import annotations

import platform as py_platform
import shutil

from .models import PackageManager

SUPPORTED_MANAGERS = {
    "linux": (
        PackageManager("apt-get", "apt-get"),
        PackageManager("dnf", "dnf"),
        PackageManager("pacman", "pacman"),
    ),
    "windows": (
        PackageManager("winget", "winget"),
        PackageManager("choco", "choco"),
    ),
    "darwin": (PackageManager("brew", "brew"),),
}


def detect_platform() -> str:
    return py_platform.system().lower()


def available_package_managers(system: str | None = None) -> list[str]:
    system = system or detect_platform()
    return [item.name for item in SUPPORTED_MANAGERS.get(system, ()) if shutil.which(item.executable)]


def detect_package_manager(preferred: str | None = None) -> str | None:
    managers = available_package_managers()
    if preferred:
        return preferred if preferred in managers else None
    return managers[0] if managers else None


def environment_snapshot() -> dict:
    import os

    return {
        "os": py_platform.system(),
        "release": py_platform.release(),
        "machine": py_platform.machine(),
        "python": py_platform.python_version(),
        "package_managers": available_package_managers(),
        "path": os.environ.get("PATH", ""),
    }
