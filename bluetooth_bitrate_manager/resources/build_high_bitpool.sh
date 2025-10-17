#!/usr/bin/env bash
set -euo pipefail

# This script rebuilds libspa-codec-bluez5.so with the high-bitpool SBC-XQ patch.

SCRIPT_DIR="$(
  cd -- "$(dirname "${BASH_SOURCE[0]}")"
  pwd
)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# Allow override via environment variable (used by GUI)
PATCH_FILE="${PATCH_FILE:-$SCRIPT_DIR/pipewire-sbc-custom-bitpool.patch}"
WORKDIR="${WORKDIR:-$HOME/.cache/pipewire-highbitpool}"
PIPEWIRE_GIT=${PIPEWIRE_GIT:-https://gitlab.freedesktop.org/pipewire/pipewire.git}
PIPEWIRE_TAG=${PIPEWIRE_TAG:-1.4.9}
INSTALL_PREFIX=${INSTALL_PREFIX:-/usr/lib/spa-0.2/bluez5}

run_privileged() {
  if command -v pkexec >/dev/null 2>&1; then
    pkexec "$@"
  else
    sudo "$@"
  fi
}

echo ">>> Using work directory: $WORKDIR"
mkdir -p "$WORKDIR"

if [[ ! -d "$WORKDIR/pipewire" ]]; then
  echo ">>> Cloning PipeWire $PIPEWIRE_TAG"
  git clone --depth 1 --branch "$PIPEWIRE_TAG" "$PIPEWIRE_GIT" "$WORKDIR/pipewire"
else
  echo ">>> Reusing existing repo; resetting to $PIPEWIRE_TAG"
  git -C "$WORKDIR/pipewire" fetch --depth 1 origin "refs/tags/$PIPEWIRE_TAG:refs/tags/$PIPEWIRE_TAG"
  git -C "$WORKDIR/pipewire" reset --hard "$PIPEWIRE_TAG"
  git -C "$WORKDIR/pipewire" clean -fdx
fi

cd "$WORKDIR/pipewire"

echo ">>> Applying high-bitpool patch"
git apply "$PATCH_FILE"

GDBUS_FALLBACK="$HOME/.local/bin/gdbus-codegen"
if [[ ! -x $GDBUS_FALLBACK ]]; then
  echo ">>> Fetching gdbus-codegen helper script"
  mkdir -p "$(dirname "$GDBUS_FALLBACK")"
  curl -s https://gitlab.gnome.org/GNOME/glib/-/raw/2.80.5/gio/gdbus-2.0/codegen/gdbus-codegen -o "$GDBUS_FALLBACK"
  chmod +x "$GDBUS_FALLBACK"
fi

if ! command -v gdbus-codegen >/dev/null 2>&1; then
  echo ">>> Installing gdbus-codegen helper into /usr/bin (requires privileges)"
  run_privileged install -m755 "$GDBUS_FALLBACK" /usr/bin/gdbus-codegen
fi

export GDBUS_CODEGEN=${GDBUS_CODEGEN:-/usr/bin/gdbus-codegen}

echo ">>> Setting up Meson build"
meson setup build -Dman=disabled -Ddocs=disabled -Dsession-managers=[] --wipe

echo ">>> Building libspa-codec-bluez5-sbc.so"
ninja -C build spa/plugins/bluez5/libspa-codec-bluez5-sbc.so

BUILD_DIR="$WORKDIR/pipewire/build"
OUTPUT_SO="$BUILD_DIR/spa/plugins/bluez5/libspa-codec-bluez5-sbc.so"
if [[ ! -f "$OUTPUT_SO" ]]; then
  echo "Failed to build $OUTPUT_SO" >&2
  exit 1
fi

BACKUP="$INSTALL_PREFIX/libspa-codec-bluez5-sbc.so.bak.$(date +%s)"
TARGET="$INSTALL_PREFIX/libspa-codec-bluez5-sbc.so"

echo ">>> Backing up current $TARGET to $BACKUP (requires privileges)"
run_privileged cp "$TARGET" "$BACKUP"

echo ">>> Installing patched libspa-codec-bluez5-sbc.so (requires privileges)"
run_privileged cp "$OUTPUT_SO" "$TARGET"

echo ">>> Restarting PipeWire stack"
systemctl --user restart pipewire pipewire-pulse wireplumber

echo
echo "Patched module installed. Reconnect your Bluetooth device and check the codec with:"
echo "  busctl --system get-property org.bluez /org/bluez/hci0/dev_<ADDR>/sep1/fdX org.bluez.MediaTransport1 Configuration"
echo
echo "If something breaks, restore the backup with:"
echo "  sudo cp $BACKUP $TARGET && systemctl --user restart pipewire pipewire-pulse wireplumber"
