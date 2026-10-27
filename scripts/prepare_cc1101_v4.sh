#!/usr/bin/env bash
# Build isolated official v4 source tree without touching any existing firmware.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT/vendor/cc1101_v4"
PIN="a732dd0e52c48973fad57e4950a11d8e2f2d6820"
PATCHES="$ROOT/patches"

if [[ -e "$DEST" ]]; then
  echo "Refusing to overwrite existing source tree: $DEST" >&2
  exit 2
fi

mkdir -p "$ROOT/vendor"
git clone --quiet https://github.com/SzczepanLeon/esphome-components.git "$DEST"
git -C "$DEST" checkout --quiet --detach "$PIN"
[[ "$(git -C "$DEST" rev-parse HEAD)" == "$PIN" ]] || {
  echo "Unexpected upstream revision" >&2
  exit 3
}

for name in \
  0001-safe-packet-decoder-and-cc1101-fifo.patch \
  0002-cc1101-long-frame-diagnostics.patch \
  0003-cc1101-stable-rxbytes.patch \
  0004-radio-diagnostics-and-key-redaction.patch \
  0005-experimental-fifo16-threshold.patch \
  0006-v4_4-clear-stale-irq.patch \
  0007-v4_5-initialize-isr-woken.patch \
  0008-v4_7-loop-only-gap-observer.patch; do
  git -C "$DEST" apply --check "$PATCHES/$name"
  git -C "$DEST" apply "$PATCHES/$name"
done

git -C "$DEST" diff --check
RADIO="$DEST/components/wmbus_radio/transceiver_cc1101.cpp"
METER="$DEST/components/wmbus_meter/wmbus_meter.cpp"
grep -Fq 'this->write_register(CC1101_MDMCFG4, 0x5C);' "$RADIO"
! grep -Fq 'this->write_register(CC1101_MDMCFG4, 0x6C);' "$RADIO"
grep -Fq 'CC1101_FIFOTHR, 0x03' "$RADIO"
! grep -Fq 'CC1101_FIFOTHR, 0x07' "$RADIO"
grep -Fq 'SHWM v4.1 FIFO16 experiment' "$RADIO"
grep -Fq 'RF_DIAG bytes=' "$RADIO"
grep -Fq 'RX_DIAG cumulative' "$DEST/components/wmbus_radio/component.cpp"
grep -Fq 'SHWM v4.4 stale IRQ clear' "$DEST/components/wmbus_radio/component.cpp"
grep -Fq 'BaseType_t xHigherPriorityTaskWoken = pdFALSE;' "$DEST/components/wmbus_radio/component.cpp"
grep -Fq 'RX_DIAG v4.7 loop_only' "$DEST/components/wmbus_radio/component.cpp"
grep -Fq 'estimate_missing_30s_periods' "$DEST/components/wmbus_radio/loop_gap_observer.h"
grep -Fq 'Key: [REDACTED]' "$METER"
! grep -Fq 'Key: %s' "$METER"

echo "CC1101 v4.7 loop-only gap observer experiment prepared: $DEST/components"
echo "Pinned upstream: $PIN"
echo "Radio BW: 325 kHz; RX FIFO threshold 16B; receive_frame() and ISR inherited unchanged from v4.5; 1s loop-only sampler."
echo "Plaintext AES startup logging disabled. No YAML or firmware modified."
git -C "$DEST" diff --stat
