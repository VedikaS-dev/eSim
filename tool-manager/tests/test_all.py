from pathlib import Path

import pytest

from esim_tool_manager.configuration import configure_environment, write_env_files
from esim_tool_manager.dependencies import dependency_order
from esim_tool_manager.manifest import load_manifest
from esim_tool_manager.models import ToolSpec, Version
from esim_tool_manager.package_managers import install_command, update_command
from esim_tool_manager.platform_support import available_package_managers
from esim_tool_manager.versioning import extract_version, satisfies

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "esim_tool_manager" / "manifest.json"


def test_version_comparison_and_policy():
    assert Version.parse("5.2") > Version.parse("5")
    assert Version.parse("4.9") < Version.parse("5")
    spec = ToolSpec("x", "x", ("--version",), True, "5", "6", None, {}, {}, (), {})
    assert satisfies("5.4", spec)
    assert not satisfies("6.0", spec)


def test_version_parsing():
    assert extract_version("ngspice-42: ngspice compiled Mar 1 2026") == "42"
    assert extract_version("kicad-cli 9.0.1") == "9.0.1"


def test_manifest_loads_and_profiles():
    specs = load_manifest(MANIFEST)
    names = {spec.name for spec in specs}
    assert {"Ngspice", "KiCad", "GHDL", "Verilator", "OpenModelica"}.issubset(names)
    assert next(spec for spec in specs if spec.name == "KiCad").depends_on == ("Ngspice",)


def test_dependency_order():
    specs = load_manifest(MANIFEST)
    kicad = next(spec for spec in specs if spec.name == "KiCad")
    ngspice = next(spec for spec in specs if spec.name == "Ngspice")
    assert [spec.name for spec in dependency_order([kicad, ngspice])] == ["Ngspice", "KiCad"]


def test_dependency_cycle_is_rejected():
    a = ToolSpec("A", "a", ("--version",), True, None, None, None, {}, {}, ("B",), {})
    b = ToolSpec("B", "b", ("--version",), True, None, None, None, {}, {}, ("A",), {})
    with pytest.raises(ValueError):
        dependency_order([a, b])


def test_unknown_dependency_is_rejected():
    a = ToolSpec("A", "a", ("--version",), True, None, None, None, {}, {}, ("missing",), {})
    with pytest.raises(ValueError):
        dependency_order([a])


def test_supported_managers_shape():
    managers = available_package_managers("linux")
    assert isinstance(managers, list)
    assert set(managers).issubset({"apt-get", "dnf", "pacman"})


def test_kicad_homebrew_uses_cask():
    kicad = next(spec for spec in load_manifest(MANIFEST) if spec.name == "KiCad")
    assert install_command(kicad, "brew") == ["brew", "install", "--cask", "kicad"]
    assert update_command(kicad, "brew") == ["brew", "upgrade", "--cask", "kicad"]


def test_apt_install_and_update_commands():
    ngspice = next(spec for spec in load_manifest(MANIFEST) if spec.name == "Ngspice")
    assert install_command(ngspice, "apt-get") == ["sudo", "apt-get", "install", "-y", "ngspice"]
    assert update_command(ngspice, "apt-get") == ["sudo", "apt-get", "install", "--only-upgrade", "-y", "ngspice"]


def test_configuration_generation(tmp_path, monkeypatch):
    monkeypatch.setattr("esim_tool_manager.configuration.default_state_dir", lambda: tmp_path / "state")
    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/ngspice")
    ngspice = next(spec for spec in load_manifest(MANIFEST) if spec.name == "Ngspice")
    config = configure_environment([ngspice], {"tool_paths": {}, "variables": {}})
    env_json, env_sh, env_ps1 = write_env_files(config)
    assert env_json.exists() and env_sh.exists() and env_ps1.exists()
    assert "export ESIM_NGSPICE" in env_sh.read_text(encoding="utf-8")
