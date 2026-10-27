# v4.17 — midpoint 100us long-frame no-progress polling

## Evidence
v4.16 test 2026-10-27 18:26:23–20:51:36 (~145.2 min):
185 decoded GAMA350 / 199 complete 326B frames; 14 failed
3of6; 0 FIFO overflows; all 199 complete frames had unstable_rxbytes=0;
835 Apator telegrams, 4 header timeouts, 2 payload read failures,
queue_drops=0. GAMA successful rate 1.274/min. Long RX bursts mean
58.4 (56–62); peak FIFO mean 35.8, max 42.

v4.9 longer historical reference ~147min: 215 decoded / 216
complete GAMA, 1 3of6 failure, 0 FIFO overflows, around 31–33
bursts per long telegram. Its observed decoded rate was 1.46/min.

## Isolated hypothesis
v4.16 reduces stable no-progress long-payload polling delay to 50us.
It significantly increases number of small FIFO reads compared
with v4.9 and leaves 14 random-position 3of6 failures. It is
UNPROVEN whether radio noise, FIFO read timing, decoding, or another
effect accounts for errors. v4.17 changes only the stable no-progress
poll interval to 100us for offset=3,length>=250, halfway between
50us and the 200us associated with overflow in earlier versions.
The 100us delay on unstable RXBYTES stays exactly unchanged, as
does the 200us stable no-progress delay for short frames. Existing
v4.16 policy helper remains in source for regression unit tests;
v4.17 helper is used in the actual driver.

Potential tradeoff: fewer SPI bursts or 3of6 errors but reduced FIFO
headroom and possible overflow. Never infer radio improvement from
passing CI alone.

No change in frequency, CC1101 setup, FIFO threshold, bandwidth,
interrupts, ISR, memory allocation, decoding, error recovery, keys,
meter IDs, Wi-Fi or YAML. No merge/release/flash/OTA.

## Verification
Native tests ensure 100us / 200us new policy and preserved 50us
v4.16 helper; prior tests pass; 15 patches against pinned upstream
SHA a732dd0e52c48973fad57e4950a11d8e2f2d6820. ESPHome 2026.10.0
compile from pinned vendor + real GitHub component.

Use external_components.source:
github://smarthomewithme/wmbus-gama350-reader@experiment/v4.17-midpoint-long-poll
and refresh: always; confirm boot log SHWM wMBus v4.17 ACTIVE.

Measure decoded and complete GAMA count, per-minute rate, 3of6,
RX_FIFO_OVERFLOW, long burst count, peak_fifo, unstable_rxbytes,
Apator successes/total, timeouts; compare 5–10min smoke and 147min
if it proves safe. Keep v4.16 and v4.9 branches unchanged.
