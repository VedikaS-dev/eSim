"""Compatibility facade for the modular eSim Tool Manager.

The public implementation is split across focused modules. This facade keeps
common imports stable for reviewers and older examples.
"""

from .audit import audit_log_path, default_state_dir, log_event
from .configuration import apply_user_environment, configure_environment, load_config, save_config, write_env_files
from .dependencies import dependency_order, dependency_report
from .detector import query_installed, run_command, status_dict
from .manifest import find_spec, load_manifest, manifest_profiles
from .models import PackageManager, ToolSpec, ToolStatus, Version
from .package_managers import check_update, install_command, update_command
from .platform_support import SUPPORTED_MANAGERS, available_package_managers, detect_package_manager, detect_platform, environment_snapshot
from .versioning import extract_version, policy_message, satisfies

__all__ = [
    "Version", "ToolSpec", "ToolStatus", "PackageManager",
    "load_manifest", "find_spec", "manifest_profiles",
    "detect_platform", "available_package_managers", "detect_package_manager", "environment_snapshot",
    "run_command", "query_installed", "status_dict", "extract_version",
    "satisfies", "policy_message", "dependency_order", "dependency_report",
    "install_command", "update_command", "check_update",
    "configure_environment", "write_env_files", "load_config", "save_config", "apply_user_environment",
    "default_state_dir", "audit_log_path", "log_event", "SUPPORTED_MANAGERS",
]
