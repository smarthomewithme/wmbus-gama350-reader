#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UPSTREAM="https://github.com/SzczepanLeon/esphome-components.git"
PIN="a732dd0e52c48973fad57e4950a11d8e2f2d6820"
DEST="$ROOT/vendor/rxfilter_270"
PATCH="$ROOT/patches/0004-cc1101-rx-bandwidth-270k.patch"

if [[ -e "$DEST" ]]; then
  echo "Already exists: $DEST" >&2
  echo "Nothing changed. Never overwrite an existing source tree automatically." >&2
  exit 2
fi

mkdir -p "$ROOT/vendor"
git clone --quiet "$UPSTREAM" "$DEST"
git -C "$DEST" checkout --quiet --detach "$PIN"
ACTUAL="$(git -C "$DEST" rev-parse HEAD)"
if [[ "$ACTUAL" != "$PIN" ]]; then
  echo "Unexpected upstream revision $ACTUAL" >&2
  exit 3
fi

git -C "$DEST" apply --check "$PATCH"
git -C "$DEST" apply "$PATCH"
git -C "$DEST" diff --check

CHANGED="$(git -C "$DEST" diff --name-only)"
if [[ "$CHANGED" != "components/wmbus_radio/transceiver_cc1101.cpp" ]]; then
  echo "Unexpected changes in variant: $CHANGED" >&2
  exit 4
fi

grep -Fq 'this->write_register(CC1101_MDMCFG4, 0x6C);' "$DEST/components/wmbus_radio/transceiver_cc1101.cpp"

echo "Prepared isolated CC1101 RX bandwidth variant (270.8 kHz)."
echo "Pinned upstream SHA: $ACTUAL"
echo "Variant components: $DEST/components"
echo "No YAML was changed. No firmware has been flashed."
git -C "$DEST" diff --stat
