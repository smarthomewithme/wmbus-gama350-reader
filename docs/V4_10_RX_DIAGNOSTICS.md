# SHWM CC1101 — v4.10 five-minute diagnostics (experimental)

This branch is based on the **exact physically tested v4.9** commit
`11b09de7f87ade632453f772c37940dbdb470c94`.
The radio receiver and its signal parameters are deliberately unmodified.

## Problem measured

In a ~147-minute v4.9 physical log the owner saw 216 complete 326-byte
GAMA350 frames and 215 successfully decoded values, 1 3-of-6 failure, no
RX FIFO overflow, no invalid FIFO count 65 and no unstable RXBYTES.
Estimated successful transmission coverage is ~73–74%, assuming the GAMA
meter broadcasts every ~30 seconds. About one in four *expected* telegrams
remains unobserved. An unseen telegram is not proof that CC1101 received
a signal or even that a transmission actually took place.

## New diagnostics

Every ~300,000 milliseconds of main-loop time (no new SPI reads / radio-task
work), emit **one** `RX_DIAG_5M` line with deltas since the previous snapshot:

- `window_ms`: actual reporting interval, rather than assuming exactly 5m.
- `irq`: receiver task notifications, **not** confirmed meter receptions.
- `header_ok` and `header_fail`: radio-level initial parsing.
- `payload_ok` and `payload_fail`: payload read outcome, not AES decoding.
- `long_frames`: full long radio payloads, **not necessarily GAMA**.
- `frame_ok` / `frame_fail`: link-frame conversion in the ESPHome main
  loop (including possible 3-of-6 conversion failures). **Not** application
  meter driver/AES/field-decode success counts.
- `queue_drops`: drop count.

The original `RX_DIAG cumulative` line stays exactly compatible with
previous logs. Native delta tests cover normal changes, boot initialization
and uint32 overflow. The helper and conversion counters are confined to
`Radio::loop()`; the receive task, FIFO, interrupt handler and CC1101
settings are unchanged.

**Interpretation caveat:** APATOR and other wireless devices contribute to
the shared IRQ/header/payload counters. A five-minute window with a missing
GAMA packet and still-high IRQ activity does not identify whether that GAMA
telegram ever triggered an IRQ. Count GAMA-specific 326-byte `Long RX`
and decoded `Telegram otrzymany od licznika prądu` events separately,
using the **same time window**; also record any decoder errors and
`RX timeout`. No formula here assumes all 326B packets must be GAMA.

## Owner-only ESPHome trial

After CI is green, replace only the GitHub source ref in the existing YAML:

```yaml
external_components:
  - source: github://smarthomewithme/wmbus-gama350-reader@experiment/v4.10-five-minute-rx-diag
    refresh: always
    components:
      - wmbus_radio
      - wmbus_common
      - wmbus_meter
      - socket_transmitter
```

Keep Wi-Fi, API, GPIO wiring, meter IDs and AES keys unchanged. Do **not**
paste credentials into issue comments or logs. This change has no automatic
OTA, production deployment, merge or release. Rollback ref:
`experiment/v4.9-stable-marcstate-eof`.

## Acceptance criteria

- Both pinned vendor and direct-from-GitHub ESPHome 2026.10.0 CI green.
- At least 60 minutes of owner logs, including 12+ `RX_DIAG_5M` windows.
- Check each five-minute delta against adjacent cumulative snapshots and
  correlate separately with GAMA 30-second scheduled slots.
- No regression in GAMA decode success, missing-slot percentage, water
  meter reads, peak FIFO, RX timeouts or receive task scheduling.
- Design the next receiver experiment only when physical evidence indicates
  a mechanism (no IRQ, rejected header, partial frame, or conversion error).
