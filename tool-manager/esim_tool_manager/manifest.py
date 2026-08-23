from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .models import ToolSpec


def load_manifest(path: Path) -> list[ToolSpec]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("schema_version") != 3:
        raise ValueError("Unsupported manifest schema_version")
    tools: list[ToolSpec] = []
    for item in raw.get("tools", []):
        tools.append(
            ToolSpec(
                name=item["name"],
                executable=item["executable"],
                version_args=tuple(item.get("version_args", ["--version"])),
                required=bool(item.get("required", False)),
                min_version=item.get("min_version"),
                max_version=item.get("max_version"),
                exact_version=item.get("exact_version"),
                package_ids=dict(item.get("package_ids", {})),
                package_type=dict(item.get("package_type", {})),
                depends_on=tuple(item.get("depends_on", [])),
                environment=dict(item.get("environment", {})),
                notes=item.get("notes", ""),
            )
        )
    if not tools:
        raise ValueError("Manifest contains no tools")
    return tools


def find_spec(manifest: Iterable[ToolSpec], name: str) -> ToolSpec:
    needle = name.strip().lower()
    for spec in manifest:
        if spec.name.lower() == needle:
            return spec
    raise KeyError(f"Unknown tool: {name}")


def manifest_profiles(path: Path) -> dict[str, list[str]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {str(key): list(value) for key, value in raw.get("profiles", {}).items()}
