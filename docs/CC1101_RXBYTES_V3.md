# CC1101 stable RXBYTES candidate — v3

## Purpose

Validate a **driver-level** candidate for GAMA 350 long T1 frames without touching the existing ESP32 GPIO wiring, meter IDs/keys, 868.95 MHz frequency or Apator sensor declarations.

The CC1101 datasheet/errata (SWRZ020E, section RX FIFO) note that reading the asynchronous RXBYTES status register while bytes are arriving may yield inconsistent values. The radio receiver must not assume that a lone snapshot is exact; a read-ahead error can read more bytes than are actually in FIFO.

References:
- https://www.ti.com/lit/er/swrz020e/swrz020e.pdf
- https://www.ti.com/lit/ds/symlink/cc1101.pdf

## Previous field observations

- Apator: short 53-byte captures decode reliably.
- GAMA 350: long 326-byte captures, 3-of-6 corruption at changing offsets.
- A diagnostic capture with 326 bytes reported 42 burst reads and RSSI around -82 dBm. The first invalid 3-of-6 symbol occurred at encoded byte 32.
- **Neither this evidence nor the successful build proves** that an inconsistent RXBYTES sample is the actual underlying defect; RF conditions remain a plausible cause.
- Source project versions are pinned. The current upstream `main` is *not* confirmed to be the last firmware that decoded GAMA 350 successfully.

## V3 changes

- Adds `cc1101_fifo.h` with a bounded two-consecutive-matching-samples reader (maximum nine SPI status reads).
- Uses this helper for regular FIFO availability checks, final-chunk confirmation, and final FIFO draining.
- When reads do not stabilize, no data is copied into the receive buffer; a timeout remains in place.
- Keeps the 64-byte physical FIFO bound and RX-overflow handling.
- Adds `unstable_rxbytes` to existing long-frame diagnostics.
- Leaves packet length calculations, sync settings, modulation, frequency, GPIO and the meter drivers unchanged.

The additional patch depends on the first safety patch **and** the second diagnostics patch. It is **not** standalone.

## Build/test sequence (no device access)

```sh
bash scripts/prepare_sources.sh
bash scripts/enable_diagnostics.sh
bash scripts/enable_stable_rxbytes.sh
g++ -std=c++17 -Wall -Wextra -Werror tests/rxbytes_stability.cpp -o /tmp/rxbytes-test
/tmp/rxbytes-test
esphome config config/wmbus-gama350.yaml
esphome compile config/wmbus-gama350.yaml
```

Use an isolated ESPHome config with placeholders, never user credentials, in CI.

## Controlled device test (only after passing CI and preserving rollback)

When explicitly authorized for an OTA test, the already-patched local component path should remain unchanged. Only update the source checkout and apply patch `0003`. Do not run `prepare_sources.sh` against an existing local `vendor/upstream`, because the script intentionally refuses to overwrite it.

The device may currently use the *upstream* GitHub component source after an A/B trial. Before an OTA test of this candidate, restore the previous **local** `external_components` source path (do not modify other YAML fields).

After OTA, capture 3–5 consecutive GAMA frames using `Long RX`, `unstable_rxbytes`, `Long frame 3of6 error`, and Apator updates. Mask startup lines that print AES keys.

A/B comparison: compare the 326-byte capture success rate, first invalid 3-of-6 position, and the number of unstable samples at the original radio placement. Do not claim an RF/driver root cause until repeatable hardware evidence exists.
