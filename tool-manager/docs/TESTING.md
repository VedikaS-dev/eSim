# Testing and Demonstration Guide

## Unit/contract tests

Install the project with its test extra:

```bash
python -m pip install -e ".[test]"
pytest
```

The tests cover:

- version comparison and policy bounds;
- version extraction;
- manifest loading;
- dependency ordering and cycle rejection;
- platform-manager detection contract;
- package command generation;
- Homebrew formula/cask behavior;
- configuration file generation.

## Safe demo sequence

```bash
python -m esim_tool_manager list
python -m esim_tool_manager env
python -m esim_tool_manager doctor
python -m esim_tool_manager install Ngspice
python -m esim_tool_manager updates
python -m esim_tool_manager configure
python -m esim_tool_manager logs --tail 20
```

The install command above is a dry-run unless `--execute` is supplied.

## Real installation test

Only run on a disposable test machine where package installation is acceptable:

```bash
python -m esim_tool_manager --package-manager apt-get install Ngspice --execute
python -m esim_tool_manager doctor
```

The manager must re-probe the executable and verify the manifest version policy.

## Cross-platform evidence

CI verifies the Python control-plane contract on Linux, Windows and macOS runners.

This is intentionally different from claiming that eSim itself has identical native support on all three platforms. The manager's adapter architecture is cross-platform; the host eSim distribution method must still be checked against upstream documentation.
