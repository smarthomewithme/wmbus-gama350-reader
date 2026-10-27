# SHWM wMBus GAMA350 CC1101 — v4.12 experimental hot path

## Hardware evidence and intended scope

- Physical v4.9: ~147 min, 216 complete 326-byte GAMA350 frames, no FIFO overflow.
- Physical v4.10: stable 65 interpreted as invalid; 12 actual overflows in ~4 min.
- Physical v4.11: the 65-count warning disappeared, but the owner reported
  11 **real** RX FIFO overflow warnings in ~100 s and zero usable frames.
- v4.11 CI: pinned-upstream compile, direct GitHub component compile,
  native tests all PASS. This did **not** prove physical reception.
- The supplied v4.11 log ends before the first five-minute diagnostic window.

## v4.12 changes

1. Remove redundant `restart_rx()` calls from the CC1101 reader on
   overflow and final-chunk failure: the outer `Radio::receive_frame()`
   already handles these errors and restarts RX exactly once.
2. On a successful FIFO read, skip the MARCSTATE SPI status probe in the same
   loop iteration; check end-of-packet on a subsequent iteration **without**
   FIFO progress. Preserve v4.9 multi-sample EOF confirmation and the
   500-ms no-progress timeout.
3. Add a boot marker `SHWM wMBus v4.12 ACTIVE` and error messages containing
   `SHWM v4.12 RX FIFO overflow` with offset, read progress, RXBYTES and
   elapsed time, to identify which path fails without disclosing keys.
4. Emit `SHWM v4.12 RX_DIAG_1M` once per minute, keeping both rolling and
   cumulative counters.
5. Preserve silicon-erratum handling of RXBYTES=65 from v4.11.

RF frequency/bandwidth, FIFO threshold, SPI pins, ISR, CC1101 register
configuration, decoding, keys, and meter IDs **are unchanged**.

## Scope and interpretation

**Not a proven fix.** Radio overflows may still originate in interrupt
scheduling, SPI latency, signal/hardware conditions or firmware caching.
A boot marker proves the intended receiver code is running; otherwise any
comparison would be invalid.

The source patch is `patches/0011-v4_12-overflow-fastpath.patch`.
Its unit tests check the MARCSTATE scheduling rule, the v4.11 FIFO boundaries
and prohibition of RF-register changes. GitHub Actions must pass on both
pinned-source and direct-install builds. The on-device result remains unknown
until the owner physically flashes the isolated branch.

## Hardware test and go/no-go

Flash only when CI is green; do not publish as stable. Keep existing radio
wiring, meter credentials, YAML settings, antenna and power supply unchanged.
Observe 5–10 minutes and capture:

- `SHWM wMBus v4.12 ACTIVE` (UART startup if captured)
- `SHWM v4.12 RX_DIAG_1M` at ~60s, 120s
- `SHWM v4.12 RX FIFO overflow` with `offset` and `received`
- `Long RX: bytes=326`, GAMA350 telegrams and meter value updates

If overflow continues, use exact `offset` and `received` to distinguish
interrupt wake-up from a payload/final-chunk issue before further RF changes.

No automatic OTA, merge, production deployment or GitHub release.
