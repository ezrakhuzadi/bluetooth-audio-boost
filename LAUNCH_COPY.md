# Launch Copy

## GitHub repository description
GTK4 + CLI toolkit that monitors PipeWire Bluetooth audio bitrates and includes an optional SBC high-bitpool rebuild. Linux only, MIT.

## Reddit post - r/linuxaudio / r/linux
**Title:** Bluetooth Bitrate Manager 0.1.0 - monitor and boost PipeWire Bluetooth audio

**Body:**
Hi folks,

I just tagged v0.1.0 of Bluetooth Bitrate Manager, a GTK4/Libadwaita desktop app paired with a CLI monitor for PipeWire Bluetooth audio. It surfaces the negotiated codec, bitrate, and SBC transport details in real time, and it ships an opt-in builder that patches PipeWire's SBC plugin for higher bitpool values (with automatic backup and restore).

Highlights:
- Live view of codecs, bitrates, channel mode, and sample rate as you connect devices.
- `bt-bitrate-monitor` CLI for remote machines or quick shell checks.
- One-click "Build and Install High Bitrate Codec" workflow that rebuilds PipeWire's SBC plugin with your preferred bitpool.
- Distribution-aware `install.sh` bootstrapper (apt, dnf, pacman, zypper, emerge) plus pipx support.

Install:
- `./install.sh` (installs distro packages, then pip install to user site)
- `pipx install bluetooth-bitrate-manager`

Repo: https://github.com/ezrakhuzadi/bluetooth-audio-boost
Docs: README + RELEASE_NOTES.md cover requirements, troubleshooting, and the SBC builder details.

I would love feedback on the GUI flow, distro coverage, and other codecs you want to see next. Enjoy the extra bitrate!

## Reddit post - r/pipewire
**Title:** Bluetooth Bitrate Manager 0.1.0 - PipeWire SBC high bitpool rebuild with live bitrate monitor

**Body:**
Hey PipeWire fans,

Sharing a tool I built for my own headphones and finally polished for release: Bluetooth Bitrate Manager 0.1.0.

What it does:
- GTK4/Libadwaita GUI that watches PipeWire and WirePlumber for Bluetooth sinks, showing the negotiated codec, sample rate, effective SBC bitpool, block length, and channels.
- `bt-bitrate-monitor` CLI that uses `pw-dump` + `pactl` parsing and the same SBC math so you can script checks or monitor via SSH.
- Optional "Build and Install High Bitrate Codec" button that runs `bluetooth_bitrate_manager/resources/build_high_bitpool.sh`. The script clones your PipeWire version, generates a patch with the requested SBC bitpool, builds `libspa-codec-bluez5-sbc.so`, and swaps it in with a backup of the original plugin.

Installer perks:
- `install.sh` figures out apt/dnf/pacman/zypper/emerge, installs GTK 4, Libadwaita, PyGObject, PipeWire tooling, and the Meson/Ninja toolchain, then pip installs the project for the current user.
- For externally managed Python setups, the script retries with `--break-system-packages` or prints instructions for pipx/virtualenv.

Grab it here: https://github.com/ezrakhuzadi/bluetooth-audio-boost
Release notes: https://github.com/ezrakhuzadi/bluetooth-audio-boost/blob/main/RELEASE_NOTES.md

If you try the SBC rebuild, let me know how it behaves on different distro PipeWire builds (especially when custom patches are in play). Issues and PRs welcome!
