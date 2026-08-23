from __future__ import annotations

import re

from .models import ToolSpec, Version

VERSION_RE = re.compile(r"(?<!\d)(\d+(?:\.\d+){0,3})(?!\d)")


def extract_version(text: str) -> str | None:
    matches = VERSION_RE.findall(text)
    if not matches:
        return None
    dotted = [m for m in matches if "." in m]
    return dotted[0] if dotted else matches[0]


def satisfies(version: str | None, spec: ToolSpec) -> bool:
    if not version:
        return False
    actual = Version.parse(version)
    if spec.exact_version and actual != Version.parse(spec.exact_version):
        return False
    if spec.min_version and actual < Version.parse(spec.min_version):
        return False
    if spec.max_version and actual >= Version.parse(spec.max_version):
        return False
    return True


def policy_message(spec: ToolSpec) -> str:
    if spec.exact_version:
        return f"Version mismatch (required exactly {spec.exact_version})"
    bounds: list[str] = []
    if spec.min_version:
        bounds.append(f">= {spec.min_version}")
    if spec.max_version:
        bounds.append(f"< {spec.max_version}")
    return f"Version outside policy ({', '.join(bounds)})" if bounds else "Version outside policy"
