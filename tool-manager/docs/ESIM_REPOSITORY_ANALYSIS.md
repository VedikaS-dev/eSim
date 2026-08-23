# eSim Repository Analysis — Evidence Behind the Tool Manager

This document records the repository areas examined to derive the tool-manager requirements. It is intentionally focused on external-tool management rather than the entire eSim codebase.

## 1. Upstream references

- Repository: https://github.com/FOSSEE/eSim
- Installation guide: https://github.com/FOSSEE/eSim/blob/master/INSTALL
- Architecture: https://github.com/FOSSEE/eSim/blob/master/ARCHITECTURE.md

## 2. What eSim currently manages around its toolchain

The current repository describes an external toolchain including:

| Component | Role | Evidence/area to inspect |
|---|---|---|
| KiCad | schematic + PCB/editor integration | `src/`, `kicadtoNgspice/`, `projManagement` |
| Ngspice | analog circuit simulation | `src/ngspiceSimulation/`, `kicadtoNgspice/` |
| NGHDL | mixed-signal interface | `nghdl/` |
| GHDL | VHDL compilation/simulation | `nghdl/install-nghdl.sh`, `nghdl/src/` |
| Verilator | Verilog/TL-Verilog workflow | `nghdl/install-nghdl.sh`, `maker/` |
| OpenModelica | optional Modelica workflow | `src/ngspicetoModelica/` |

## 3. Installation mechanisms

### eSim itself

The current `INSTALL` document describes:

- Flatpak as the recommended route for broad Linux distribution support.
- Ubuntu native installation through the top-level `install-eSim.sh` script.
- Windows installation through a Windows installer.
- Docker as a separate distribution route.

The same document states that Flatpak does not include NGHDL, Makerchip and SKY130 PDK, and notes host integration limitations. This demonstrates why "eSim is installed" is not equivalent to "every eSim capability is ready".

### NGHDL

The repository contains an NGHDL installer and describes it as an automated installer for GHDL, Verilator and Ngspice. That is a concrete example of a composite dependency group.

### IHP

The `ihp/` directory contains:

- `ihp-install-script.sh`
- `install-ngspice-latest.sh`
- `.spiceinit`

The latter script builds a current Ngspice from source for the IHP PDK use case. This shows that not every eSim tool installation can be represented as a simple OS package install.

## 4. Application integration points worth tracing

The repository areas that are most useful for a Tool Manager study are:

```text
src/projManagement/Validation.py
src/projManagement/Kicad.py
src/configuration/Appconfig.py
src/ngspiceSimulation/NgspiceWidget.py
nghdl/install-nghdl.sh
nghdl/src/ngspice_ghdl.py
nghdl/src/model_generation.py
nghdl/src/ghdlserver/
src/ngspicetoModelica/
src/maker/
ihp/install-ngspice-latest.sh
```

The goal when reading these files is not to understand every application algorithm. The goal is to determine:

1. which external executable is invoked;
2. which command-line arguments/path conventions are assumed;
3. whether PATH or configuration is required;
4. what happens when the tool is missing;
5. whether a tool is core or optional.

## 5. Compatibility evidence

The upstream issue tracker contains a concrete compatibility failure: eSim 2.5 installation on Ubuntu 25.10 can fail while building GHDL because the system LLVM version is newer than the GHDL release being built. This demonstrates that robust management must consider the surrounding toolchain, not only the presence of an executable.

Reference: https://github.com/FOSSEE/eSim/issues/451

## 6. What this prototype addresses

| Repository observation | Prototype response |
|---|---|
| Different OS installation paths | package-manager adapters |
| Tool version drift | version policy in manifest |
| Missing executables | PATH-aware detector / doctor |
| External dependencies | directed dependency graph |
| User-specific paths | configuration state + environment files |
| Manual update checks | manager-specific update probes |
| Risky installation commands | dry-run by default |
| Need for diagnosis | `doctor` + JSON output |
| Need to understand actions | JSONL audit log |

## 7. Remaining gaps

The prototype does not yet implement a complete eSim compatibility knowledge base. It also does not attempt universal rollback, source-build orchestration for every optional flow, or direct replacement of the upstream eSim Tool Manager.

These are deliberate future extensions rather than claims of full production parity.
