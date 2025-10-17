# Contributing to Bluetooth Bitrate Manager

Thanks for your interest in improving Bluetooth Bitrate Manager! This document explains how to get a development environment running, what kinds of changes are welcome, and how to submit pull requests.

## Getting started
- **Know the stack**: the project targets Linux desktops running PipeWire + WirePlumber (BlueZ). Make sure you have a device you can pair for testing.
- **Clone the repository** and install the package in editable mode:
  ```bash
  python3 -m pip install --user --upgrade build
  python3 -m pip install --user -e .
  ```
- **Launch the components**:
  - GUI: `python3 -m bluetooth_bitrate_manager.gui`
  - CLI monitor: `python3 -m bluetooth_bitrate_manager.monitor --once`
- **Installer smoke test** (optional): run `./install.sh` inside a disposable VM/container for your distribution to validate dependency detection.

Working inside a virtual environment or using `pipx inject` keeps system Python clean, but the project also supports `--user` installs.

## Coding guidelines
- **Style**: follow the existing code style (PEP 8 with 88-100 character lines). Type hints are encouraged for new code.
- **Imports**: standard library first, third-party packages second, local modules last.
- **Logging/UI**: the GUI uses Libadwaita patterns; keep long-running work on threads and update the UI through GLib idlers.
- **Error handling**: fail loudly with actionable error messages, especially when invoking subprocesses or privileged commands.
- **Strings**: prefer f-strings; use single quotes unless the string contains one already.
- **Resources**: keep executable scripts in `bluetooth_bitrate_manager/resources/` and add them to `MANIFEST.in` if new files need packaging.

## Testing changes
Automated tests are currently minimal. Please validate changes manually:
- Pair a Bluetooth device and confirm the GUI updates in real time.
- Run `bt-bitrate-monitor --once` to verify CLI output.
- If you touch the installer or SBC builder, run them end-to-end in a VM, keeping an eye on sudo/pkexec prompts.

If you add automated tests, store them under `tests/` and document how to run them in this file.

## Submitting a pull request
1. Fork the repository and create a topic branch.
2. Make sure `pyproject.toml` and any packaging metadata stay in sync (version, entry points, package data).
3. Update documentation (README, release notes) if behaviour or user flow changes.
4. Run through the manual smoke tests above.
5. Push your branch and open a pull request that:
   - Links to any relevant issues.
   - Describes the problem and the fix.
   - Lists manual verification steps.

Maintainers will review your PR, request adjustments if necessary, and merge once it is ready. Thank you for helping Bluetooth Bitrate Manager reach more listeners!
