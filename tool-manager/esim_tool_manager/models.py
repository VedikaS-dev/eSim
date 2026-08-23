from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Version:
    parts: tuple[int, ...]

    def __post_init__(self) -> None:
        if not self.parts:
            raise ValueError("Version must contain at least one component")
        if len(self.parts) < 4:
            object.__setattr__(self, "parts", self.parts + (0,) * (4 - len(self.parts)))

    @classmethod
    def parse(cls, value: str) -> "Version":
        import re
        text = value.strip().lstrip("vV")
        match = re.search(r"\d+(?:\.\d+){0,3}", text)
        if not match:
            raise ValueError(f"Invalid version: {value!r}")
        return cls(tuple(int(x) for x in match.group(0).split(".")))

    def __str__(self) -> str:
        return ".".join(str(x) for x in self.parts).rstrip(".0") or "0"


@dataclass(frozen=True)
class ToolSpec:
    name: str
    executable: str
    version_args: tuple[str, ...]
    required: bool
    min_version: str | None
    max_version: str | None
    exact_version: str | None
    package_ids: dict[str, str]
    package_type: dict[str, str]
    depends_on: tuple[str, ...]
    environment: dict[str, str]
    notes: str = ""


@dataclass(frozen=True)
class PackageManager:
    name: str
    executable: str


@dataclass
class ToolStatus:
    name: str
    installed: bool
    version: str | None
    path: str | None
    meets_policy: bool
    package_manager: str | None
    dependencies_ok: bool
    message: str
