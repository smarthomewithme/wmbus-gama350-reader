#!/usr/bin/env bash
# Prepare the isolated CC1101 long-frame FIFO candidate. No changes to the
# existing device, ESPHome YAML, original source trees, or radio firmware.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UPSTREAM_URL="https://github.com/SzczepanLeon/esphome-components.git"
PIN="a732dd0e52c48973fad57e4950a11d8e2f2d6820"
DEST="$ROOT/vendor/cc1101_v3"
PATCH_DIR="$ROOT/patches"

if [[ -e "$DEST" ]]; then
  echo "Refusing to overwrite existing $DEST" >&2
  exit 2
fi

mkdir -p "$ROOT/vendor"
git clone --quiet "$UPSTREAM_URL" "$DEST"
git -C "$DEST" checkout --quiet --detach "$PIN"
ACTUAL="$(git -C "$DEST" rev-parse HEAD)"
if [[ "$ACTUAL" != "$PIN" ]]; then
  echo "Unexpected upstream revision $ACTUAL" >&2
  exit 3
fi

for patch in \
  "0001-safe-packet-decoder-and-cc1101-fifo.patch" \
  "0002-cc1101-long-frame-diagnostics.patch" \
  "0003-cc1101-stable-rxbytes.patch"; do
  git -C "$DEST" apply --check "$PATCH_DIR/$patch"
  git -C "$DEST" apply "$PATCH_DIR/$patch"
done

git -C "$DEST" diff --check

DRIVER="$DEST/components/wmbus_radio/transceiver_cc1101.cpp"
if [[ "$(grep -Fc 'this->write_register(CC1101_MDMCFG4, 0x5C);' "$DRIVER")" != "1" ]]; then
  echo "Filter register must be the baseline 0x5C (325 kHz)." >&2
  exit 4
fi
if grep -Fq 'this->write_register(CC1101_MDMCFG4, 0x6C);' "$DRIVER"; then
  echo "Unexpected 270 kHz filter experiment in isolated candidate." >&2
  exit 5
fi
grep -Fq 'unstable_rxbytes=' "$DRIVER"
test -f "$DEST/components/wmbus_radio/cc1101_fifo.h"

echo "CC1101 v3 isolated candidate prepared successfully."
echo "Upstream pinned SHA: $ACTUAL"
echo "Source directory: $DEST/components"
echo "Receiver filter: 325 kHz (MDMCFG4=0x5C)"
echo "Applied: FIFO safety, long-frame diagnostics, stable RXBYTES"
echo "No ESPHome configuration or device firmware changed."
git -C "$DEST" diff --stat
