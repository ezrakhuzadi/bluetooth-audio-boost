# Flatpak Installation

## Automatic Repository (Recommended)

This repository automatically builds and publishes Flatpak packages to GitHub Pages on every commit.

### Add the repository:
Download the public key first:
```bash
wget https://ezrakhuzadi.github.io/bluetooth-bitrate-manager/bluetooth-bitrate.gpg
```

Then add the remote:
```bash
flatpak remote-add --user --gpg-import=bluetooth-bitrate.gpg bluetooth-bitrate https://ezrakhuzadi.github.io/bluetooth-bitrate-manager
```

### Install the app:
```bash
flatpak install --user bluetooth-bitrate com.github.ezrakhuzadi.BluetoothBitrateManager
```

> Note: The repository is hosted directly at `https://ezrakhuzadi.github.io/bluetooth-bitrate-manager` (without a `/repo` suffix).

### Run the app:
```bash
flatpak run com.github.ezrakhuzadi.BluetoothBitrateManager
```

### Update the app:
```bash
flatpak update com.github.ezrakhuzadi.BluetoothBitrateManager
```

## Direct Download

Download the latest `.flatpak` bundles from:
- https://ezrakhuzadi.github.io/bluetooth-bitrate-manager/com.github.ezrakhuzadi.BluetoothBitrateManager-x86_64.flatpak
- https://ezrakhuzadi.github.io/bluetooth-bitrate-manager/com.github.ezrakhuzadi.BluetoothBitrateManager-aarch64.flatpak

Install with:
```bash
flatpak install ./com.github.ezrakhuzadi.BluetoothBitrateManager-<arch>.flatpak
```

## Build Requirements for SBC Rebuild

The Flatpak can rebuild SBC codecs, but requires build tools on your **host system**:

```bash
sudo pacman -S git meson ninja gcc pkgconf pipewire
```

The build script will run on your actual system (outside the sandbox) when you click "Build and Install High Bitrate Codec" in the app.

## Permissions

The Flatpak has these permissions:
- Wayland/X11 display access
- PipeWire/PulseAudio audio
- Bluetooth D-Bus access
- Home directory access (for copying build scripts)
- Host command execution (for SBC rebuild via flatpak-spawn)
- Bluetooth hardware device access

## Uninstall

```bash
flatpak uninstall com.github.ezrakhuzadi.BluetoothBitrateManager
flatpak remote-delete bluetooth-bitrate
```

## Maintainer signing setup

GitHub Actions signs the repository metadata, so a GPG key must be configured.

### Generate signing key (one-time)

```bash
gpg --quick-gen-key "Bluetooth Bitrate Manager (Flatpak) <noreply@example.com>" rsa4096 sign 2y
gpg --list-secret-keys --keyid-format=long  # note the key ID
```

### Export secrets for CI

```bash
# Private key for FLATPAK_GPG_PRIVATE_KEY secret
gpg --export-secret-keys --armor YOURKEYID > FLATPAK_GPG_PRIVATE_KEY.asc

# Public key published to users
gpg --export --armor YOURKEYID > bluetooth-bitrate.gpg
```

Add repository secrets:
- `FLATPAK_GPG_PRIVATE_KEY`: contents of `FLATPAK_GPG_PRIVATE_KEY.asc`
- `FLATPAK_GPG_PASSPHRASE`: optional passphrase used when generating the key

Publish `bluetooth-bitrate.gpg` alongside the Flatpak repo (it is uploaded automatically by CI).

When the key is rotated, update both secrets and the published `.gpg` file, then re-run the workflow.
