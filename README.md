# Bluetooth Bitrate Manager

Bluetooth Bitrate Manager is a GTK4/Libadwaita desktop companion and CLI monitor that surfaces real-time codec stats for your Bluetooth audio devices on PipeWire. It also ships an opt-in builder that patches PipeWire's SBC plugin for higher bitpool values while keeping the original binary backed up.

## Table of contents
- [Highlights](#highlights)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Build a high-bitrate SBC codec](#build-a-high-bitrate-sbc-codec)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [License](#license)

## Highlights
- Works with modern Linux desktops that use PipeWire/WirePlumber and BlueZ - no PulseAudio hacks required.
- Libadwaita interface auto-refreshes when devices connect, change codec, or negotiate a new bitrate.
- `bt-bitrate-monitor` CLI prints the same negotiated SBC parameters that the GUI shows, so you can script or SSH into remote machines.
- One-click "Build and Install High Bitrate Codec" action patches PipeWire's SBC plugin with your chosen bitpool and restores the original file on uninstall.
- `install.sh` bootstraps system packages for Debian/Ubuntu, Fedora, Arch, openSUSE, and Gentoo before installing the Python package to your user site.
- MIT licensed and versioned - this repository is ready for packaging and the initial 0.1.0 release.

## Requirements
- Linux with PipeWire >= 0.3.x and WirePlumber (or another BlueZ-compatible session manager).
- Python 3.9 or newer.
- System GTK dependencies: PyGObject (`python3-gi`), GTK 4, and Libadwaita.
- PipeWire/BlueZ utilities: `pactl`, `pw-dump`, and `busctl`.
- Optional SBC rebuild: compiler toolchain (`git`, `meson`, `ninja`, `gcc`, `pkg-config`, `curl`).

## Installation

### Option 1 - install script (recommended)
The repository ships `install.sh`, which requests sudo once, installs missing system dependencies, and performs a user-level pip install:

```bash
./install.sh
```

The script keeps the sudo ticket alive during the install and drops a `.desktop` launcher into `~/.local/share/applications/`.

### Option 2 - pipx
```bash
pipx install bluetooth-bitrate-manager
```

You may still need to install the GTK runtime packages via your distribution if they are not present.

### Option 3 - pip (user site)
```bash
python3 -m pip install --user bluetooth-bitrate-manager
```

After installation the following entry points are available on your PATH:
- `bluetooth-bitrate-gui` - start the GTK application.
- `bt-bitrate-monitor` - run the terminal monitor.

## Usage

### Launch the desktop app
Run `bluetooth-bitrate-gui` from a terminal or find "Bluetooth Bitrate Manager" in your desktop menu.

The app automatically:
- Lists currently connected Bluetooth audio sinks.
- Displays negotiated codec, bitrate, channel mode, block length, and sample rate.
- Refreshes live when devices connect/disconnect or the transport renegotiates.
- Shows a helper pane to configure high-bitpool SBC defaults and trigger the rebuild script.

### Run the terminal monitor
```bash
bt-bitrate-monitor
```

Optional flags:
- `-o/--once` - show the current state and exit (useful inside shell scripts).
- `-w/--watch` - refresh periodically to follow negotiations in real time.

Behind the scenes the monitor combines `pactl` data with SBC transport parsing from `bluetooth_bitrate_manager.bitrate_utils` to report the same numbers as the GUI.

## Build a high-bitrate SBC codec

From the GUI choose **Build and Install High Bitrate Codec**. The app runs `bluetooth_bitrate_manager/resources/build_high_bitpool.sh`, which:
1. Clones PipeWire at the host's current version.
2. Generates a SBC patch with your requested bitpool.
3. Builds `libspa-codec-bluez5-sbc.so` and installs it system-wide, backing up the stock binary alongside it.

The script needs elevated privileges; the app detects `pkexec` or `sudo`, caches credentials, and keeps them alive for long builds. You can revert to the backed-up plugin at any time from the same dialog.

Prefer the CLI? Run the script directly:

```bash
sudo bluetooth_bitrate_manager/resources/build_high_bitpool.sh
```

## Troubleshooting
- **No devices detected:** confirm PipeWire is running and that your Bluetooth headset shows up in `pactl list sinks`.
- **Missing GTK modules:** install `python3-gi`, `gtk4`, and `libadwaita` packages for your distribution.
- **SBC builder fails:** make sure build tools (`meson`, `ninja`, `gcc`, `pkg-config`, `curl`, `git`) are installed and that `/usr` is writable with sudo/pkexec.
- **Externally managed Python:** if pip refuses to install system-wide, use `pipx`, a virtual environment, or rerun the installer which retries with `--break-system-packages` when available.

## Development
Create a virtual environment or work inside your user site-packages:

```bash
python3 -m pip install --user --upgrade build
python3 -m pip install --user -e .

# Launch the GUI from source
python3 -m bluetooth_bitrate_manager.gui

# Exercise the monitor
python3 -m bluetooth_bitrate_manager.monitor --once
```

The codebase follows standard library formatting (88-100 character lines) and aims to keep functions pure where possible - please match the existing style. Run `./install.sh` on a dev box if you want to confirm the bootstrapper works across distributions.

See `CONTRIBUTING.md` for pull request guidelines and `RELEASE_NOTES.md` for the current changelog.

## License
MIT (c) Ezra
