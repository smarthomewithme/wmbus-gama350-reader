# CC1101 v4.16 — 50us no-progress delay for long payloads only

## Test evidence
v4.15 physical test (18:12:21–18:18:46): no decoded GAMA or Apator,
no complete GAMA frames, 62 true hardware FIFO overflow logs
(40 raw=0xBE; 22 raw=0xC1), all with received=0. The once-per-minute
diagnostic returned payload_ok=0 and queue_drops=0. The v4.15 change
removing the 100us unstable RXBYTES backoff for long payloads is **rejected**.

## Single hypothesis, based on v4.14
v4.14 (~8 min) received 4 decoded GAMA350 and 31 Apator, but lost
long payloads to FIFO overflow near end. v4.13 already skips the 200us
backoff after progress. v4.16 retains all v4.14 settings and sampling,
including the **100us delay after unstable RXBYTES**, and makes a
single scheduling change: on stable no-progress iterations when
offset == 3 and length >=250, wait 50us instead of 200us. Other
reads remain at 200us. This could reduce FIFO headroom loss without
the immediate retry behavior that coincided with v4.15 failure.
This is not proven until physical test; faster polling could cause
additional CPU/SPI overhead.

## Patch ancestry and gates
Directly based on v4.14 commit 633096eb9dbc73b32a3ff1db1cbef55107079d3e.
Does NOT contain v4.15 patch. Pinned upstream unchanged.
14 patches total (through v4.14 plus v4.16 only). Native boundary/static
tests, git patch checks and ESPHome 2026.10.0 builds on pinned vendor
and direct GitHub external_components source.

## Use
Use source github://smarthomewithme/wmbus-gama350-reader@experiment/v4.16-long-idle-poll,
refresh always. Leave frequency 868.950 MHz, keys, pins, gain, FIFOTHR
and all YAML settings unchanged. Confirm boot marker
SHWM wMBus v4.16 ACTIVE; monitor Apator early, then GAMA complete vs
decoded counts, offset=3 long-payload overflow, unstable RXBYTES,
bursts, short payload overflow and queue drops. Success requires
both meters functional and GAMA efficiency improving, not merely
one correctly decoded frame.

No merge/release/OTA performed.
