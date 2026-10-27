# CC1101 v4.15: bounded fast retries for unstable RXBYTES during long payloads

## Physical evidence
v4.14 eight-minute log: 5 complete 326B GAMA frames, 4 decoded, 1 3of6
failure, 28 overflow logs including 5 while reading a 323-byte GAMA
payload. 31 water telegrams; no queue drops. GAMA full frames reported
4-11 unstable_rxbytes events and ~15-20 FIFO bursts.

## Isolated hypothesis
read_stable_rxbytes() already probes CC1101_RXBYTES a bounded number
of times, requiring two matching status samples; on unstable status
read_in_task() also calls delayMicroseconds(100) before retrying.
During 323-byte GAMA RX that extra 100us may consume FIFO headroom.
v4.15 skips that 100us pause only for offset == 3 && length >= 250.
It retains the delay for headers and short frames (incl. Apator).
It does NOT alter stable sampling, FIFO burst limits, final-byte
retention, MARCSTATE EOF confirmation, normal 200us no-progress
backoff, ISR, RF registers, gain, pre-IRQ Packet allocation or decoder.

The high-priority receiver may consume more CPU when RXBYTES stays
unstable. A real CC1101 test is necessary: no improvement is assumed.

## Gates and measurement
All 14 sequential patches on pinned upstream a732dd0e52c48973fad57e4950a11d8e2f2d6820;
native regression and boundary tests; static patch-scope test;
ESPHome 2026.10.0 build from pinned tree and actual GitHub branch.
No keys, deploy, OTA or merge.
Switch only external_components.source to
github://smarthomewithme/wmbus-gama350-reader@experiment/v4.15-fast-unstable-retry
and leave refresh: always. Check 'SHWM wMBus v4.15 ACTIVE'
on boot. Measure >5-10 minutes: correct vs complete GAMA frames,
3of6 errors, long-payload and short/zero-byte overflow separately,
bursts, unstable_rxbytes and Apator rate. Compare with v4.14 and
best verified v4.9 rate; interrupts are not count of GAMA broadcasts.
