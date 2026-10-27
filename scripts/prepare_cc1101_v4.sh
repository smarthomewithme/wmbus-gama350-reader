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
  0008-v4_9-confirm-marcstate-eof.patch \
  0009-v4_10-five-minute-rx-diag.patch \
  0010-v4_11-rxbytes65-prefetch.patch \
  0011-v4_12-overflow-fastpath.patch \
  0012-v4_13-progress-poll.patch \
  0013-v4_14-preallocate-packet-before-irq.patch; do
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
grep -Fq 'SHWM v4.9 MARCSTATE EOF confirmation' "$RADIO"
grep -Fq 'confirm_marcstate_eof(' "$RADIO"
grep -Fq 'inline bool confirm_marcstate_eof(' "$DEST/components/wmbus_radio/cc1101_fifo.h"
grep -Fq 'kCc1101MaxReportedRxBytes = 65' "$DEST/components/wmbus_radio/cc1101_fifo.h"
grep -Fq 'rx_fifo_count_plausible(available)' "$RADIO"
grep -Fq 'rx_fifo_complete_read(' "$RADIO"
grep -Fq 'rx_should_probe_marcstate(' "$RADIO"
grep -Fq 'SHWM v4.12 RX FIFO overflow' "$RADIO"
grep -Fq 'SHWM v4.13 post-drain polling' "$RADIO"
grep -Fq 'rx_should_backoff_after_drain(made_progress)' "$RADIO"
grep -Fq 'SHWM wMBus v4.12 ACTIVE' "$DEST/components/wmbus_radio/component.cpp"
grep -Fq 'SHWM wMBus v4.13 ACTIVE' "$DEST/components/wmbus_radio/component.cpp"
grep -Fq 'SHWM wMBus v4.14 ACTIVE' "$DEST/components/wmbus_radio/component.cpp"
grep -Fq 'SHWM v4.14 packet preallocation' "$DEST/components/wmbus_radio/component.cpp"
grep -Fq 'SHWM v4.12 RX_DIAG_1M' "$DEST/components/wmbus_radio/component.cpp"
grep -Fq 'RF_DIAG bytes=' "$RADIO"
grep -Fq 'RX_DIAG cumulative' "$DEST/components/wmbus_radio/component.cpp"
grep -Fq 'SHWM v4.10 RX_DIAG_5M' "$DEST/components/wmbus_radio/component.cpp"
grep -Fq 'frame_conversion_failed_' "$DEST/components/wmbus_radio/component.cpp"
grep -Fq 'inline RxDiagSnapshot rx_diag_delta(' "$DEST/components/wmbus_radio/rx_diag_window.h"
grep -Fq 'SHWM v4.4 stale IRQ clear' "$DEST/components/wmbus_radio/component.cpp"
grep -Fq 'BaseType_t xHigherPriorityTaskWoken = pdFALSE;' "$DEST/components/wmbus_radio/component.cpp"
grep -Fq 'Key: [REDACTED]' "$METER"
! grep -Fq 'Key: %s' "$METER"

echo "CC1101 v4.14 preallocated packet experiment prepared: $DEST/components"
echo "Pinned upstream: $PIN"
echo "Radio BW: 325 kHz; RX FIFO threshold 16B; v4.9 MARCSTATE confirmation retained; RXBYTES=65 supported; v4.13 progress polling retained; packet constructed before IRQ wait."
echo "Plaintext AES startup logging disabled. No YAML or firmware modified."
git -C "$DEST" diff --stat
