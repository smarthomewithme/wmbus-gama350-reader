# CC1101 v4.18 — 150us idle-poll probe for long payloads

## Physical baseline
v4.17 run 2026-10-27 21:31:30 to 2026-10-28 00:02:59 (~151.5 min):
214 complete 326-byte GAMA350 frames; 205 decoded, 9 3of6 failures;
0 RX FIFO overflows; 140 successful Apator telegrams; all 214
complete GAMA frames reported unstable_rxbytes=0. In first 147 minutes,
198 correct GAMA from 207 complete. Typical 57–59 FIFO bursts,
highest peak_fifo=45B.

Historical v4.9 147-minute run: 215 decoded / 216 complete GAMA;
1 3of6 failure, zero overflows. v4.16 ~145 minutes:
185 decoded / 199 complete GAMA, 14 3of6 failures, zero overflows.

## One hypothesis
v4.17 does stable no-progress polling every 100us for long payloads
(offset == 3 && length >= 250). v4.18 tests **150us**, positioned
between that and the 200us idle polling used in earlier versions.
100us RXBYTES-unstable retry, 200us short-frame/header polling,
bounded RXBYTES reads, FIFO thresholds, MARCSTATE EOF confirmation,
pre-IRQ allocation, v4.9 recovery, RF band 868.950MHz, sync,
frequency, gain, 3of6 decoding, keys, wiring and YAML do not change.

No assumption is made that 150us will improve physical reception.
Monitor lost GAMA/Apator, 3of6, bursts, peak FIFO, and overflow.

## Process
Sixteen ordered patches on pinned upstream
a732dd0e52c48973fad57e4950a11d8e2f2d6820
(v4.9–v4.14 + v4.16–v4.18; rejected v4.15 omitted).
Native and contract test plus ESPHome 2026.10.0 compile from
prepared vendor and actual GitHub external_components source.
No merge, public release, OTA or flash. Keep previous versions.

Use source:
github://smarthomewithme/wmbus-gama350-reader@experiment/v4.18-long-idle-150us
with refresh: always. Confirm boot marker SHWM wMBus v4.18 ACTIVE.
