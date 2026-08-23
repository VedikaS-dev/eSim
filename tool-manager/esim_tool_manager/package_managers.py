from __future__ import annotations

from .detector import run_command
from .models import ToolSpec


def _package(spec: ToolSpec, package_manager: str) -> str:
    try:
        return spec.package_ids[package_manager]
    except KeyError as exc:
        raise ValueError(f"No package mapping for {spec.name} with {package_manager}") from exc


def install_command(spec: ToolSpec, package_manager: str) -> list[str]:
    package = _package(spec, package_manager)
    kind = spec.package_type.get(package_manager, "formula")
    if package_manager == "apt-get":
        return ["sudo", "apt-get", "install", "-y", package]
    if package_manager == "dnf":
        return ["sudo", "dnf", "install", "-y", package]
    if package_manager == "pacman":
        return ["sudo", "pacman", "-S", "--noconfirm", package]
    if package_manager == "winget":
        return [
            "winget", "install", "--id", package, "--exact",
            "--accept-source-agreements", "--accept-package-agreements"
        ]
    if package_manager == "choco":
        return ["choco", "install", package, "-y", "--no-progress"]
    if package_manager == "brew":
        return ["brew", "install", "--cask", package] if kind == "cask" else ["brew", "install", package]
    raise ValueError(f"Unsupported package manager: {package_manager}")


def update_command(spec: ToolSpec, package_manager: str) -> list[str]:
    package = _package(spec, package_manager)
    kind = spec.package_type.get(package_manager, "formula")
    if package_manager == "apt-get":
        return ["sudo", "apt-get", "install", "--only-upgrade", "-y", package]
    if package_manager == "dnf":
        return ["sudo", "dnf", "upgrade", "-y", package]
    if package_manager == "pacman":
        return ["sudo", "pacman", "-S", "--noconfirm", package]
    if package_manager == "winget":
        return [
            "winget", "upgrade", "--id", package, "--exact",
            "--accept-source-agreements", "--accept-package-agreements"
        ]
    if package_manager == "choco":
        return ["choco", "upgrade", package, "-y", "--no-progress"]
    if package_manager == "brew":
        return ["brew", "upgrade", "--cask", package] if kind == "cask" else ["brew", "upgrade", package]
    raise ValueError(f"Unsupported package manager: {package_manager}")


def check_update(spec: ToolSpec, package_manager: str) -> dict:
    if package_manager not in spec.package_ids:
        return {
            "name": spec.name,
            "supported": False,
            "available": None,
            "message": "No package mapping",
        }

    package = _package(spec, package_manager)
    if package_manager == "apt-get":
        proc = run_command(["apt-cache", "policy", package])
        installed = candidate = None
        for line in proc.stdout.splitlines():
            key, _, value = line.partition(":")
            if key.strip() == "Installed":
                installed = value.strip()
            elif key.strip() == "Candidate":
                candidate = value.strip()
        available = bool(
            candidate and candidate != "(none)"
            and installed not in (None, "(none)")
            and candidate != installed
        )
        return {
            "name": spec.name,
            "supported": proc.returncode == 0,
            "available": available,
            "installed": installed,
            "candidate": candidate,
            "message": "Update available" if available else "Up to date",
        }

    if package_manager == "dnf":
        proc = run_command(["dnf", "check-update", package])
        return {
            "name": spec.name,
            "supported": proc.returncode in (0, 100),
            "available": proc.returncode == 100,
            "message": "Update available" if proc.returncode == 100 else "Up to date or metadata unavailable",
        }

    if package_manager == "pacman":
        proc = run_command(["pacman", "-Qu", package])
        available = proc.returncode == 0 and bool(proc.stdout.strip())
        return {
            "name": spec.name,
            "supported": proc.returncode in (0, 1),
            "available": available,
            "message": "Update available" if available else "Up to date",
        }

    if package_manager == "brew":
        kind = spec.package_type.get(package_manager, "formula")
        args = ["brew", "outdated", "--cask", package] if kind == "cask" else ["brew", "outdated", "--formula", package]
        proc = run_command(args)
        available = proc.returncode == 0 and bool(proc.stdout.strip())
        return {
            "name": spec.name,
            "supported": proc.returncode == 0,
            "available": available,
            "message": "Update available" if available else "Up to date",
        }

    if package_manager == "choco":
        proc = run_command(["choco", "outdated", "--limit-output", "--ignore-pinned"])
        available = any(line.split("|", 1)[0].lower() == package.lower() for line in proc.stdout.splitlines())
        return {
            "name": spec.name,
            "supported": proc.returncode in (0, 1),
            "available": available,
            "message": "Update available" if available else "Up to date or not found",
        }

    if package_manager == "winget":
        proc = run_command([
            "winget", "upgrade", "--id", package, "--exact", "--accept-source-agreements",
        ])
        lower = f"{proc.stdout}\n{proc.stderr}".lower()
        not_found = "no applicable upgrade found" in lower or "no package found" in lower
        available = proc.returncode == 0 and not not_found and package.lower() in lower
        return {
            "name": spec.name,
            "supported": proc.returncode == 0 or not_found,
            "available": available,
            "message": "Update available" if available else "No applicable update found",
        }

    return {
        "name": spec.name,
        "supported": False,
        "available": None,
        "message": "Unsupported package manager",
    }
