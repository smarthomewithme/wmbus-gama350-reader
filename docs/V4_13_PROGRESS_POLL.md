# SHWM wMBus GAMA350 — v4.13 progress-responsive FIFO polling

## Single hypothesis

The hardware v4.12 log shows 28 complete 326-byte GAMA frames (27 decoded,
one 3of6 error) but 448 RX FIFO overflow reports over approximately 76 minutes.
Of these, 76 are in the 323-byte GAMA payload read; a large fraction occur
near the end. In the 28 completed frames, mean bursts=13.04,
median peak FIFO=59.5, mean unstable RXBYTES=6.96.

The transceiver still waits `delayMicroseconds(200)` after **each** iteration,
even when a successful burst just drained the FIFO. When RXBYTES sampling is
unstable or near capacity, this unnecessary pause can increase the next
iteration's occupancy and shorten the remaining FIFO headroom.

**Change only one receiver scheduling rule:** after an iteration that
successfully reads a positive byte count, immediately loop and poll RXBYTES
again. Keep the existing 200 us pause when no progress was made.
The existing 100 us delay after an unstable RXBYTES sample is unchanged.

No change to radio frequency (868.950 MHz), MDMCFG4=0x5C,
FIFO threshold=0x03, AGC, interrupts, ISR, MARCSTATE EOF confirmation,
RXBYTES=65 handling, 3of6 decoder, AES redaction or queue behavior.
v4.10/v4.11/v4.12 patches remain in place. v4.9 remains the physically proven
baseline, not a downgrade target.

## Evidence and acceptance

- v4.9 physical reference: 216 complete GAMA frames in ~147 minutes, 215
  decoded, one 3of6 error, zero reported FIFO overflows.
- v4.12 supplied test: 28 complete in ~76 minutes; 27 decoded, one 3of6 error,
  276 ordinary + 172 final overflow logs; 76 are while receiving 323B GAMA
  payloads. No software queue drops in the 76 complete one-minute windows.
- Native test asserts the changed backoff decision, plus 0/1/63/64/65/66
  FIFO count boundaries and multiple remaining lengths. Static contracts
  prohibit any RF register or ISR edits.
- CI must apply all 12 patches against pinned upstream
  `a732dd0e52c48973fad57e4950a11d8e2f2d6820`, compile ESPHome 2026.10.0
  using both vendored and actual GitHub branch sources, and pass diff checks.

**Physical outcome unknown until tested**. Start with 5-10 minutes; if overflow
rate decreases sharply, continue for >=60 minutes (ideally 2-3 hours). Compare
complete/decoded GAMA, 3of6, GAMA-payload overflows, burst distribution,
peak_fifo, unstable_rxbytes, RSSI, FREQEST, Apator and one-minute RX diagnostics.
Do not count an IRQ or header fail as necessarily one missed GAMA transmission.

## ESPHome test ref (owner flashes, never CI)

```yaml
external_components:
  - source: github://smarthomewithme/wmbus-gama350-reader@experiment/v4.13-progress-poll
    refresh: always
    components:
      - wmbus_radio
      - wmbus_common
      - wmbus_meter
      - socket_transmitter
```

Rollback/reference: `experiment/v4.9-stable-marcstate-eof`.
No branch merging, release or OTA performed by this experiment.
