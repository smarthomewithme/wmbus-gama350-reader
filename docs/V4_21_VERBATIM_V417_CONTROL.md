# v4.21 — exact v4.17 source, fresh ESPHome cache / build control

## Why this control exists
The v4.17 hardware run (151.5min) decoded 205 of 214 complete
GAMA350 frames, had 0 FIFO overflows, and both GAMA350 and Apator
worked. Later that same firmware ran for over 3h continuously
with cumulative payload_fail=0.

By contrast, THREE unrelated experimental branches v4.18, v4.19
and v4.20 all failed to receive even one payload, including short
Apator telegrams. `raw=0xBE` or `0xC1` RX FIFO overflow occurred
with `received=0`. The changes in v4.18 and v4.20 only touched
long-frame timing and therefore could not directly explain the
short-frame or header failures. All ESPHome builds passed GitHub CI.

**Control purpose:** distinguish regression tied to modified radio
code from firmware build/cache/setup conditions.

## This version changes NO embedded C/C++ source
Base: `experiment/v4.17-midpoint-long-poll` at
`3cc700587f9eaa86610ebf5cb061f2c6f48b3b43`.
- Same pinned upstream: `a732dd0e52c48973fad57e4950a11d8e2f2d6820`.
- EXACT SAME 15 patches, in exact same order, byte-for-byte.
- No new C++ patch; no change to RF registers, SPI, CC1101 FIFO,
  ISR, timings, decode3of6, meter IDs or ESPHome YAML.
- Changes only the Python `_CACHE_LAYOUT` fingerprint
  (forces ESPHome GitHub component bootstrap to re-prepare sources)
  and Python preparation log string.
- Adds contract test checking Git blob hashes of every original
  patch from v4.17, plus documentation and CI branch tracking.
- On the device the old `SHWM wMBus v4.17 ACTIVE` startup marker
  remains intentional (because compiled source is identical).
  **There is deliberately no v4.21 radio firmware marker.**
- Watch compile output for `SHWM v4.21 CONTROL:` to verify the
  bootstrap path; also check built-at timestamp after OTA.

## Strict protocol
1. In ESPHome, use `Clean Build Files` for wmbus-reader, then
   compile and flash this control with:
   `github://smarthomewithme/wmbus-gama350-reader@experiment/v4.21-verbatim-v417-control`
   and `refresh: always`. The other YAML values stay unchanged.
   This test intentionally rebuilds the same source as v4.17.
2. Monitor for 2–3 minutes. Need both GAMA and Apator decoded;
   zero repeated `received=0`/overflow.
3. If PASS, it suggests repeated failures were related to changed
   source/build or timing conditions, not a guaranteed specific
   code line. Keep v4.17 as confirmed-good runtime.
4. If FAIL, software-behavior differences between versions cannot
   explain this control failure; investigate actual build/cache,
   CC1101 initialization and power, IRQ/startup. First verify
   exact external-components source resolved and clean build.
   Optionally fully power-cycle ESP32+CC1101 to isolate retained
   state; do not change radio parameters blindly.

No merge, release, flash or device access from CI.
