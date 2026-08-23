# Automated eSim Tool Manager — Design Document

## 1. Problem

eSim relies on several external EDA/simulation programs. Their installation methods, executable names, package-manager identifiers, versions and environment assumptions vary across operating systems.

The manager maintains a declarative desired state and reconciles it with the actual host.

## 2. Architecture

```text
CLI / future GUI
       |
       v
Manager Service
       |
       +--> Manifest / Policy
       +--> Detector
       +--> Dependency Resolver
       +--> Planner
       +--> Package Adapters
       +--> Executor
       +--> Verifier
       +--> Configuration
       +--> Audit Log
```

### Core separation

- **Policy:** what eSim needs.
- **Detection:** what is actually installed.
- **Planning:** what should change.
- **Execution:** how to change it.
- **Verification:** whether the desired state was achieved.
- **Configuration:** how eSim should find the tools.
- **Audit:** what happened.

This prevents platform-specific commands from leaking into the high-level policy layer.

## 3. Capability matrix

| Requirement | Implementation |
|---|---|
| 1. Tool installation | Platform adapters for APT, DNF, Pacman, WinGet, Chocolatey and Homebrew; post-install verification |
| 2. Updates | Manager-specific update probes and upgrade command builders |
| 3. Configuration | Executable discovery, persisted JSON config, shell/PowerShell environment generation and optional profile application |
| 4. Dependency checker | Directed dependency graph, topological ordering, cycle detection and dependency health reports |
| 5. UI | CLI commands, human-readable tables, JSON output and audit logs |
| 6. Additional | Cross-platform adapter layer and CI matrix |

## 4. eSim-aware tool model

The manifest models:

- Ngspice — core circuit simulation backend.
- KiCad — schematic/PCB integration.
- GHDL — VHDL capability for NGHDL/mixed-signal workflows.
- Verilator — Verilog/TL-Verilog capability and NGHDL-related workflows.
- OpenModelica — optional Modelica workflow.

Profiles separate core from optional capability sets.

## 5. Installation lifecycle

```text
request
  |
  v
resolve tools
  |
  v
resolve dependency order
  |
  v
inspect installed state
  |
  +---- compliant ---> SKIP
  |
  v
build package-manager command
  |
  v
DRY RUN (default) or EXECUTE
  |
  v
re-probe executable
  |
  v
verify version policy
```

## 6. Update lifecycle

Package-manager semantics differ, therefore update probes live in the package-manager adapter:

- APT: compare installed/candidate versions from `apt-cache policy`.
- DNF: interpret `dnf check-update`.
- Pacman: inspect `pacman -Qu`.
- Homebrew: inspect `brew outdated`.
- Chocolatey: inspect `choco outdated`.
- WinGet: query the exact package identifier with `winget upgrade`.

## 7. Configuration lifecycle

The manager discovers executable paths using PATH resolution, persists state under `~/.esim-tool-manager`, and generates:

- `config.json`
- `environment.json`
- `environment.sh`
- `activate.ps1`

On POSIX systems the optional `--apply` operation updates a clearly delimited block in `~/.profile`. On Windows it generates a PowerShell activation script rather than trying to perform fragile permanent PATH mutation.

## 8. Safety model

1. Dry-run is default.
2. Commands are argument arrays, not shell command strings.
3. Package IDs are exact manifest values.
4. Real execution is followed by verification.
5. Audit records are JSONL and include timestamps/results.
6. Unsupported operations fail explicitly.

## 9. eSim integration boundary

The manager should sit above eSim's application modules rather than duplicating simulation logic:

```text
eSim UI / startup
       |
       v
Tool Manager
       |
       +--> health/doctor
       +--> install/update
       +--> configuration
       +--> status for GUI/CI
```

The current submission remains standalone so it can be evaluated as a proof of concept without changing the upstream eSim application.

## 10. Future production extensions

- Full eSim-release compatibility matrix.
- Composite capabilities such as NGHDL as first-class dependency graphs.
- Exact lock files for reproducible toolchains.
- Source-build adapters for toolchains such as IHP's latest Ngspice flow.
- Artifact hashes/signatures.
- Offline cache.
- Package-manager-aware rollback where supported.
- Qt GUI consuming the same service layer.
- Direct integration into eSim's evolving Tool Manager backend.
