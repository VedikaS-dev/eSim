from __future__ import annotations

from .detector import query_installed
from .manifest import find_spec
from .models import ToolSpec


def dependency_order(specs: list[ToolSpec]) -> list[ToolSpec]:
    by_name = {item.name.lower(): item for item in specs}
    output: list[ToolSpec] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(spec: ToolSpec) -> None:
        key = spec.name.lower()
        if key in visited:
            return
        if key in visiting:
            raise ValueError(f"Dependency cycle involving {spec.name}")
        visiting.add(key)
        for dependency in spec.depends_on:
            if dependency.lower() in by_name:
                visit(by_name[dependency.lower()])
            else:
                raise ValueError(f"Dependency {dependency!r} for {spec.name!r} is not declared in manifest")
        visiting.remove(key)
        visited.add(key)
        output.append(spec)

    for spec in specs:
        visit(spec)
    return output


def dependency_report(spec: ToolSpec, specs: list[ToolSpec], package_manager: str | None = None) -> dict:
    results = []
    for dependency_name in spec.depends_on:
        dependency = find_spec(specs, dependency_name)
        status = query_installed(dependency, package_manager)
        results.append(
            {
                "name": dependency.name,
                "ok": status.meets_policy,
                "version": status.version,
                "message": status.message,
            }
        )
    return {
        "tool": spec.name,
        "ok": all(item["ok"] for item in results),
        "dependencies": results,
    }
