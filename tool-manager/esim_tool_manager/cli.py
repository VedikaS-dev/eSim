from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .audit import audit_log_path
from .manager import ToolManager
from .platform_support import environment_snapshot

ROOT = Path(__file__).resolve().parent
DEFAULT_MANIFEST = ROOT / "manifest.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Automated lifecycle manager for the eSim external toolchain")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--package-manager", help="Force a specific package-manager adapter")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit machine-readable JSON")

    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="List managed tools and policies")
    sub.add_parser("doctor", help="Check tools, versions and dependencies")
    sub.add_parser("updates", help="Check update availability")
    sub.add_parser("env", help="Show platform and package-manager information")
    sub.add_parser("config", help="Show persisted configuration")
    sub.add_parser("logs", help="Show recent audit events").add_argument("--tail", type=int, default=20)

    configure = sub.add_parser("configure", help="Generate eSim tool paths/environment files")
    configure.add_argument("--execute", action="store_true", help="Persist generated configuration")
    configure.add_argument("--apply", action="store_true", help="Apply manager-owned shell configuration")

    for action in ("install", "update"):
        cmd = sub.add_parser(action, help=f"Plan or execute {action} actions")
        cmd.add_argument("tool", nargs="+", help="Tool names from the manifest")
        cmd.add_argument("--execute", action="store_true", help="Actually modify the system; default is dry-run")

    return parser


def _emit(data: object, as_json: bool) -> None:
    if as_json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(data)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manager = ToolManager(args.manifest, args.package_manager)
    except (OSError, ValueError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"Initialization error: {exc}", file=sys.stderr)
        return 2

    try:
        if args.command == "list":
            data = manager.list_tools()
            if args.as_json:
                _emit(data, True)
            else:
                for item in data:
                    policy = item["exact_version"] or \
                        (f">= {item['min_version']}" if item["min_version"] else "any")
                    print(f"{item['name']:12} {item['executable']:14} {policy:12} "
                          f"{'REQUIRED' if item['required'] else 'optional'}")
            return 0

        if args.command == "doctor":
            payload = manager.doctor()
            if args.as_json:
                _emit(payload, True)
            else:
                for item in payload["tools"]:
                    state = "OK" if item["meets_policy"] else ("MISS" if not item["installed"] else "WARN")
                    print(f"[{state:4}] {item['name']:12} {item['version'] or '-':10} "
                          f"{item['path'] or '-':45} {item['message']}")
                print(f"\nPackage manager: {payload['selected_package_manager'] or 'none detected'}")
                print(f"Required toolchain healthy: {payload['required_ok']}")
            return 0 if payload["required_ok"] else 1

        if args.command == "updates":
            data = manager.updates()
            _emit(data, args.as_json)
            return 0

        if args.command == "env":
            data = environment_snapshot()
            data["selected_package_manager"] = manager.package_manager
            _emit(data, True)
            return 0

        if args.command == "config":
            from .configuration import load_config
            _emit(load_config(), True)
            return 0

        if args.command == "configure":
            data = manager.configuration(apply=args.apply, persist=args.execute)
            _emit(data, True)
            return 0

        if args.command == "logs":
            path = audit_log_path()
            if not path.exists():
                print("No audit log yet.")
                return 0
            for line in path.read_text(encoding="utf-8").splitlines()[-args.tail:]:
                print(line)
            return 0

        if args.command in {"install", "update"}:
            result = manager.apply(args.command, args.tool, args.execute)
            if args.as_json:
                _emit(result, True)
            else:
                for item in result["results"]:
                    if item["action"] == "skip":
                        print(f"[SKIP] {item['tool']}: {item['reason']}")
                        continue
                    label = "RUN " if args.execute else "PLAN"
                    print(f"[{label}] {' '.join(item['command'])}")
                    if args.execute:
                        print(f"[VERIFY] {item['tool']}: {item.get('version', '-') or '-'} — {item.get('message', 'failed')}")
            return result["returncode"]

    except (KeyError, ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
