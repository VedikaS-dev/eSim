# Verification Report

## What is verified in this repository

The project has automated tests for:

- Version parsing and ordering.
- Minimum/exact/max version policy.
- Manifest schema and eSim-oriented profiles.
- Dependency ordering and cycle rejection.
- Package-manager command generation.
- Homebrew formula/cask distinction.
- Configuration file generation.
- Cross-platform adapter discovery contract.

## What is not claimed as fully verified here

- Real package installation on all operating systems.
- Every package ID in every external registry.
- Universal rollback.
- Complete eSim release/toolchain compatibility knowledge.
- Native macOS eSim distribution parity.

These require real platform environments and/or upstream integration testing.

## Reproducible local verification

```bash
python -m pip install -e ".[test]"
pytest
python -m esim_tool_manager list
python -m esim_tool_manager doctor
python -m esim_tool_manager configure
```

For a live package-manager test, run the commands on the target OS and save the terminal output in the presentation/demo evidence.
