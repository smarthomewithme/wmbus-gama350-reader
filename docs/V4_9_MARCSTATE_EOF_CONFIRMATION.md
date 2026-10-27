# SHWM wMBus/CC1101 — v4.9 MARCSTATE EOF confirmation (experimental)

This is an isolated experiment, based on **exact v4.5** commit
`c95f692e3a8bb357730e91f58b2cd45eba8aa29c`.
It intentionally contains **none of the v4.6/v4.7/v4.8 RXBYTES experiments**.

## Why this experiment?

A v4.5 physical sample after rollback captured 14 full 326-byte GAMA frames
in ~8.5 minutes, 11 decoded and 3 with 3-of-6 errors. No unstable
RXBYTES, invalid FIFO count 65 or FIFO overflow appeared in that sample.
Thus, v4.5 is a reasonable *baseline*, not a guaranteed perfect receiver.

The pinned CC1101 driver previously exited the in-progress FIFO read after
**one** MARCSTATE sample indicating IDLE or RX_END. TI's CC1101 errata
(SWRZ020E) warns that MARCSTATE can be inconsistent during active reception.
This change checks suspected end-of-frame states for **two consecutive
identical terminal samples**, with at most three additional status reads.
An intermediate active/non-terminal sample cancels the premature end
decision. Normal receive states incur no additional SPI reads.

*Hypothesis, not proven root cause:* this might prevent some truncated
frames. It cannot recover bad RF signal, a 3-of-6 error in fully received
payload data, or an actual FIFO overflow.

## What stays exactly as in v4.5?

- Pinned SzczepanLeon upstream: `a732dd0e52c48973fad57e4950a11d8e2f2d6820`.
- All seven existing patches; new patch 0008 changes only the
  MARCSTATE end-of-frame check and a small, testable inline helper.
- CC1101 MDMCFG4 `0x5C` (325 kHz bandwidth), FIFO threshold `0x03`
  (16 bytes), radio/ISR scheduling, 200 µs poll, 500 ms progress timeout,
  RXBYTES stabilization, FIFO read/drain policy and 3-of-6 decoder.
- No automatic flash/OTA, publication, or production deployment.

## Test via ESPHome (owner-controlled)

Change **only the branch ref** in the existing `external_components` source:

```yaml
external_components:
  - source: github://smarthomewithme/wmbus-gama350-reader@experiment/v4.9-stable-marcstate-eof
    refresh: always
    components:
      - wmbus_common
      - wmbus_radio
      - wmbus_meter
      - socket_transmitter
```

Keep all working pins, meter IDs, AES keys, Wi-Fi and other YAML unchanged.
Install only after the Draft PR checks finish green and the owner elects
to test. **Rollback:** return the source ref to
`experiment/v4.5-isr-woken-init`, compile/install, and compare equivalent
sample durations.

## Physical A/B protocol

Record at least 60 minutes per firmware, ideally comparable time of day
and placement (GAMA expected approximately every 30 seconds). Compare:

1. Full 326-byte GAMA frames / nominal 30-second slots.
2. Successfully decoded GAMA values / nominal slots.
3. 3-of-6 decoder errors / complete long frames.
4. `RX timeout`, `Invalid RX FIFO count`, overflow and `unstable_rxbytes`.
5. `Long RX` bursts, peak FIFO, duration, RSSI/FREQEST and APATOR stability.

CI tests the helper, correct code composition and ESPHome compilation; only
physical A/B reception can determine whether v4.9 improves actual reliability.
Reference: [Texas Instruments CC1101 errata SWRZ020E](https://www.ti.com/lit/er/swrz020e/swrz020e.pdf).
