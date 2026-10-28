# Paired v4.21/v4.23 read-only firmware build comparison

Physical rationale: same ESP32 and ESPHome 2026.10.1:
- Working **v4.21** ~165 min: 214/231 GAMA350 326B frames decoded (92.64%),
  883 Apator telegrams, ZERO RX FIFO overflow and 0 unstable RXBYTES;
  two header timeouts; RSSI −69..−74 dBm.
- **v4.23** fails before reading header bytes with CC1101 RXBYTES=0xC1.
  Its IRQ-to-task wake measurement last 32us, max 61us. This did not
  capture before-IRQ latency and cannot establish root cause.
- v4.22 also fails, hardware MARCSTATE=0x11 confirmed.

This workflow does not modify device firmware. It compiles pinned commits
v4.21 `a11d6f8` and v4.23 `1bc9174` with exactly **ESPHome 2026.10.1**
and identical synthetic CI secrets. Both use their actual GitHub
external_components sources, including their exact bootstrap preparation.

Success criterion: the ONLY compiled component source change must be
`wmbus_radio/component.cpp` containing v4.23 IRQ timestamp and
deferred main-loop reporting. Report captures exact unified source diff,
ELF/BIN/MAP sizes and SHA256 fingerprints. A changed binary is
expected, but DOES NOT prove how/why CC1101 overflows. Differing
build artifacts can reflect non-reproducible build IDs/paths.

No radios, real keys, production meter IDs, CI publish, OTA, merges,
or deployments. The artifact is report text only.

This is a prerequisite to selecting a next single-variable physical
test, not a new v4.24 firmware or claim that the cause is resolved.
