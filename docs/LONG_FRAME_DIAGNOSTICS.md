# Long-frame CC1101 diagnostics

## Field observation (2026-10-26)

This is a summary of a local device log; no private meter identifier, key, or raw captured frame is stored here.

| Observed event | Count |
|---|---:|
| Successfully decoded water meter frames, 53 raw bytes | 37 |
| Electricity meter frame captures, 326 raw bytes | 9 |
| Successfully decoded electricity meter frames | 0 |
| Electricity frames with valid first 10-byte CRC block | 7 |
| Short unrecognized 8-byte captures | 29 |
| CC1101 timeouts waiting for the initial three bytes | 10 |
| Explicit RX FIFO overflow warnings | 0 |

The first invalid 3-of-6 symbol in the nine 326-byte captures was observed at encoded byte positions 36, 33, 38, 13, 36, 32, 22, 3, and 36, respectively. The visible raw message is truncated to the first 235 bytes by the logger output buffer; this does **not** imply that the radio retrieved only 235 bytes. The receiver reports 326 bytes for each electricity frame.

The earlier packet-pointer and last-byte FIFO fixes compile and preserve reception of the shorter water telegrams, but **do not resolve this electricity frame failure**.

A valid first CRC block in seven captures and later invalid 3-of-6 symbols favor corruption occurring in or before the raw radio path rather than an AES, meter ID, or Home Assistant field-mapping problem. The current observations do not prove whether the fault is SPI, CC1101 FIFO sequencing, radio interference, or the CC1101 modem configuration.

## Optional diagnostic build

This patch is an additional *instrumentation* layer on top of the first candidate patch, not a promised fix. It records compact measurements **after** receiving a long frame:

- First invalid encoded byte offset (without logging packet contents).
- Total RX burst count, peak FIFO occupancy, and receive duration.
- First eight completed RX burst end offsets.
- RSSI for the raw long frame even when frame decoding fails.

It leaves the CC1101 pins, packet settings, and application sensors unchanged.

For an ESPHome installation whose working project resides under `/config/esphome`:

```sh
cd /config/esphome/wmbus-gama350-reader
git pull
bash scripts/enable_diagnostics.sh
```

Run ESPHome configuration validation and Clean Build Files. Firmware flashing is **not** performed by the script. Do not flash without retaining a rollback copy.

Use the existing `CC1101: DEBUG` logger setting. After an authorized OTA, capture a few long frames. Compare `[D][CC1101]: Long RX` with `[W][3of6]: Long frame 3of6 error`. Also verify that the water meter still updates.

**Never upload actual API/Wi-Fi/OTA credentials, AES keys, or unredacted startup logs to a public issue.** A boot dump may print AES keys even if they are stored in ESPHome secrets.

## Follow-up decision

Correlate the invalid-symbol offsets with radio burst boundaries and signal strength. If faults align with burst boundaries, isolate burst-read timing/SPI handling; if not, compare RF reception and modem settings using a controlled experiment. Keep each change independently revertible.
