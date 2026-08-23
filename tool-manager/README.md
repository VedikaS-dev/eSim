# Automated eSim Tool Manager

A Python proof-of-concept that manages the external eSim toolchain across Linux, Windows and macOS package-manager environments.

The manager is intentionally designed as a **policy-driven control plane** rather than a collection of shell scripts:

```text
Desired tool state
        ↓
   Detect / Diagnose
        ↓
   Version policy
        ↓
 Dependency resolution
        ↓
      PLAN
        ↓
 Install / Update
        ↓
    Verify again
        ↓
 Configure eSim paths
        ↓
   Audit the result
```

## What this prototype demonstrates

| Task requirement | Prototype capability |
|---|---|
| 1. Installation | APT, DNF, Pacman, WinGet, Chocolatey and Homebrew adapters; version-aware planning; post-install verification |
| 2. Updates | Package-manager-specific update probes and upgrade commands |
| 3. Configuration | Executable discovery, persisted configuration, POSIX environment file, PowerShell activation script, optional `~/.profile` integration |
| 4. Dependencies | Dependency graph, ordering, cycle detection and policy-aware `doctor` |
| 5. UI | CLI inventory, health check, update view, configuration, JSON output and JSONL audit logs |
| 6. Additional | Cross-platform adapter architecture and GitHub Actions matrix |

The task requires any two requirements; this prototype intentionally demonstrates all six at a proof-of-concept level.

## eSim-specific scope

Current eSim documentation identifies a toolchain around **KiCad, Ngspice, GHDL, Verilator/NGHDL and optional OpenModelica workflows**. The upstream repository also has multiple installation mechanisms and platform-specific packaging. The manager therefore models a core profile and optional capability profiles instead of treating every external component as mandatory.

The manifest is intentionally data-driven so tool versions, package IDs, dependencies and environment variables can evolve without rewriting the manager core.

## Repository structure

```text
esim-tool-manager/
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
│   ├── DESIGN.md
│   ├── ESIM_REPOSITORY_ANALYSIS.md
│   ├── TESTING.md
│   └── VERIFICATION.md
├── esim_tool_manager/
│   ├── __main__.py
│   ├── cli.py
│   ├── core.py                 # compatibility facade
│   ├── models.py               # Version / ToolSpec / status models
│   ├── versioning.py           # version extraction + policy
│   ├── manifest.py             # declarative manifest loader
│   ├── platform_support.py     # OS/package-manager detection
│   ├── detector.py             # PATH + executable/version probes
│   ├── dependencies.py         # dependency ordering and reports
│   ├── package_managers.py     # APT/DNF/Pacman/WinGet/Choco/Brew
│   ├── executor.py             # dry-run / mutation boundary
│   ├── configuration.py        # persisted paths + environment files
│   ├── audit.py                # JSONL action log
│   └── manifest.json            # eSim tool policy and profiles
├── tests/
│   └── test_all.py
├── pyproject.toml
├── requirements.txt
├── README.md
└── .gitignore
```

## Quick start

### 1. Clone/extract

```bash
git clone <your-private-fork>
cd esim-tool-manager
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install the project and test dependency

```bash
python -m pip install -e ".[test]"
```

### 4. Run tests

```bash
pytest
```

### 5. Inspect the manager

```bash
python -m esim_tool_manager list
python -m esim_tool_manager env
python -m esim_tool_manager doctor
```

### 6. Demonstrate a safe installation plan

```bash
python -m esim_tool_manager install Ngspice
```

Nothing is changed because the default is **dry-run**.

### 7. Execute a real installation

Only on a disposable/test machine where package installation is acceptable:

```bash
python -m esim_tool_manager install Ngspice --execute
```

The manager re-probes the executable and checks the version policy after execution.

### 8. Check updates

```bash
python -m esim_tool_manager updates
```

### 9. Configure detected tool paths

```bash
python -m esim_tool_manager configure
python -m esim_tool_manager configure --execute
```

To apply a manager-owned shell block:

```bash
python -m esim_tool_manager configure --apply
```

### 10. Inspect audit logs

```bash
python -m esim_tool_manager logs --tail 20
```

## Force a package manager

The manager can automatically select an available package manager, but a reviewer can force one for reproducible planning:

```bash
python -m esim_tool_manager --package-manager apt-get install Ngspice
```

## JSON / automation mode

```bash
python -m esim_tool_manager --json doctor
python -m esim_tool_manager --json list
python -m esim_tool_manager --json install Ngspice
```

## Design decisions

### Declarative policy

`manifest.json` describes what the eSim toolchain should look like. The Python control plane does not contain one giant branch per tool.

### Planning before mutation

Installation/update commands are generated and displayed before a user explicitly requests `--execute`.

### Verify after mutation

A successful package-manager exit code is not accepted as the final proof. The manager re-discovers the executable and verifies the configured version policy.

### Cross-platform adapters

The core logic is OS-independent; package-manager adapters translate generic install/update requests into platform-specific commands.

### Security boundary

Commands are represented as argument arrays and passed to `subprocess.run()` without unnecessary shell interpolation. The project does not execute downloaded scripts through `shell=True`.

## Known limitations

This is a screening-task proof of concept, not a production replacement for the evolving eSim Tool Manager. In particular:

1. Package identifiers in the manifest must be validated against the target distribution/package source before production rollout.
2. Version parsing intentionally targets common CLI version outputs; some tools may require tool-specific parsers.
3. Deep compatibility constraints (for example GHDL/LLVM combinations) are not yet represented as a full compatibility matrix.
4. The dependency graph is tool-level; operating-system package dependency resolution remains delegated to the native package manager.
5. Universal rollback across package managers is not implemented.
6. macOS adapter support is a manager capability; current eSim distribution/documentation should be checked before claiming native macOS eSim support.

These are documented as future production extensions rather than hidden behind inflated claims.

## eSim research references

- Upstream eSim: https://github.com/FOSSEE/eSim
- eSim INSTALL: https://github.com/FOSSEE/eSim/blob/master/INSTALL
- eSim architecture: https://github.com/FOSSEE/eSim/blob/master/ARCHITECTURE.md
- eSim downloads: https://esim.fossee.in/download
- Ngspice: https://ngspice.sourceforge.io/
- KiCad CLI: https://docs.kicad.org/9.0/en/cli/cli.html
- GHDL: https://ghdl.github.io/ghdl/
- Python subprocess: https://docs.python.org/3/library/subprocess.html
- Python packaging version specifiers: https://packaging.python.org/en/latest/specifications/version-specifiers/
- Debian APT guide: https://www.debian.org/doc/manuals/apt-guide/
- Microsoft WinGet: https://learn.microsoft.com/en-us/windows/package-manager/winget/
- Homebrew: https://brew.sh/
- pytest: https://docs.pytest.org/en/stable/
- GitHub Actions: https://docs.github.com/en/actions

## License

GPL-3.0-or-later for this submission prototype. Review the upstream eSim licensing terms before merging code directly into the main eSim repository.
