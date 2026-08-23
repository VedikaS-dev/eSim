from __future__ import annotations

from pathlib import Path

from .audit import log_event
from .configuration import apply_and_log, configure_environment, load_config, save_config, write_env_files
from .dependencies import dependency_order, dependency_report
from .detector import query_installed
from .executor import execute
from .manifest import find_spec, load_manifest
from .models import ToolSpec
from .package_managers import check_update, install_command, update_command
from .platform_support import detect_package_manager, environment_snapshot


class ToolManager:
    def __init__(self, manifest_path: Path, package_manager: str | None = None) -> None:
        self.manifest_path = manifest_path
        self.tools = load_manifest(manifest_path)
        self.package_manager = package_manager or detect_package_manager()

    def list_tools(self) -> list[dict]:
        return [
            {
                "name": spec.name,
                "executable": spec.executable,
                "required": spec.required,
                "min_version": spec.min_version,
                "max_version": spec.max_version,
                "exact_version": spec.exact_version,
                "depends_on": list(spec.depends_on),
                "package_managers": sorted(spec.package_ids),
                "notes": spec.notes,
            }
            for spec in self.tools
        ]

    def doctor(self) -> dict:
        ordered = dependency_order(self.tools)
        statuses = [query_installed(spec, self.package_manager) for spec in ordered]
        reports = {spec.name: dependency_report(spec, self.tools, self.package_manager) for spec in self.tools}
        required_names = {spec.name for spec in self.tools if spec.required}
        required_ok = all(status.meets_policy and reports[status.name]["ok"] for status in statuses if status.name in required_names)
        payload = {
            "platform": environment_snapshot(),
            "selected_package_manager": self.package_manager,
            "tools": [status.__dict__ for status in statuses],
            "dependencies": reports,
            "required_ok": required_ok,
        }
        log_event("doctor", {"required_ok": required_ok})
        return payload

    def updates(self) -> list[dict]:
        if not self.package_manager:
            raise RuntimeError("No supported package manager detected")
        results = [check_update(spec, self.package_manager) for spec in self.tools if self.package_manager in spec.package_ids]
        log_event("updates", {"package_manager": self.package_manager, "results": results})
        return results

    def configuration(self, apply: bool = False, persist: bool = False) -> dict:
        generated = configure_environment(self.tools, load_config())
        env_json, env_sh, env_ps1 = write_env_files(generated)
        result = {
            "configuration": generated,
            "files": [str(env_json), str(env_sh), str(env_ps1)],
            "persisted": False,
        }
        if persist or apply:
            save_config(generated)
            result["persisted"] = True
        if apply:
            result["applied_to"] = str(apply_and_log(generated))
        return result

    def plan(self, action: str, names: list[str]) -> list[dict]:
        if not self.package_manager:
            raise RuntimeError("No supported package manager detected")
        requested = [find_spec(self.tools, name) for name in names]
        ordered = dependency_order(requested)
        plan: list[dict] = []
        for spec in ordered:
            current = query_installed(spec, self.package_manager)
            if action == "install" and current.meets_policy:
                plan.append({"tool": spec.name, "action": "skip", "reason": "already satisfies policy"})
                continue
            command = install_command(spec, self.package_manager) if action == "install" else update_command(spec, self.package_manager)
            plan.append({"tool": spec.name, "action": action, "command": command})
        return plan

    def apply(self, action: str, names: list[str], execute_changes: bool = False) -> dict:
        plan = self.plan(action, names)
        results = []
        code = 0
        for item in plan:
            if item["action"] == "skip":
                results.append(item)
                continue
            command = item["command"]
            result_code = execute(command, dry_run=not execute_changes)
            item_result = dict(item)
            item_result["returncode"] = result_code
            if execute_changes and result_code == 0:
                spec = find_spec(self.tools, item["tool"])
                after = query_installed(spec, self.package_manager)
                item_result["verified"] = after.meets_policy
                item_result["version"] = after.version
                item_result["message"] = after.message
                if not after.meets_policy:
                    code = max(code, 1)
            else:
                item_result["verified"] = None
            code = max(code, result_code)
            results.append(item_result)
        log_event("apply", {"action": action, "execute": execute_changes, "result_code": code})
        return {"plan": plan, "results": results, "returncode": code}
