# Release Notes

## v0.1.0 - 2025-10-17

### Highlights
- First public release of Bluetooth Bitrate Manager.
- GTK4/Libadwaita desktop app that auto-discovers PipeWire Bluetooth sinks and displays negotiated codec, bitrate, channel mode, block length, and sample rate.
- `bt-bitrate-monitor` CLI tool for headless monitoring and scripting.
- Integrated "Build and Install High Bitrate Codec" workflow that patches PipeWire's SBC plugin with a custom bitpool and backs up the vendor binary.
- Distribution-aware `install.sh` bootstrapper that installs GTK, PipeWire, and build dependencies before performing a user-level pip install.

### Packaging
- Source distribution and wheel metadata managed via `pyproject.toml`.
- `bluetooth_bitrate_manager/resources/` packaged for runtime access (desktop file, SBC builder script, patch template).
- Desktop entry installed to `~/.local/share/applications/` by the installer.

### Known issues
- PipeWire rebuild requires sudo or pkexec; users without elevated privileges must copy the rebuilt plugin manually.
- The CLI currently relies on `pactl`/`pw-dump`; environments without these utilities will show empty results.
- Automated tests are minimal - use manual validation when contributing.
