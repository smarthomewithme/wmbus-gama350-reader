# v4.19 — earlier CC1101 RX FIFO interrupt (8B) on v4.17 baseline

## Observation (v4.18)
Physical run 2026-10-28 00:09:33–00:17:05: no valid GAMA350
or Apator, 30 logged FIFO overflows, all received=0. Among these,
10 times offset=3,length=323 raw=0xBE; 7 times offset=3,length=50,
8 times offset=3,length=5, 5 header failures offset=0,length=3
raw=0xC1. Last counters: payload_ok=0,payload_fail=23,
header_ok=23,header_fail=5,queue_drops=0. Thus data was lost
before first byte of payload/header, including short frames,
not explained by v4.18's long-payload-only 100us -> 150us change.
Possible causes include late RX scheduling/interrupts or radio
state; not proven. All v4.18 CI green: CI cannot assess actual RF.

## Isolated experiment
Use directly the **v4.17** parent (205 correct of 214 full GAMA
over 151.5 min, zero FIFO overflows, Apator functioning), not
v4.18. Modify only CC1101 FIFOTHR RX threshold 16B (0x03)
to 8B (0x01), yielding earlier GPIO4 threshold IRQ wakeup.
Preserve 868.950 MHz, modem BW, gain, RX packet encoding,
100us v4.17 long-payload no-progress polling, 200us short and
header no-progress, 100us unstable retry, pre-IRQ Packet
allocation, FIFO safety, MARCSTATE EOF double confirmation,
decoder, AES redaction and all YAML. No redefinition of FIFO
counts or other state machine changes.

**Unproven hypothesis:** 0.64ms earlier IRQ (at 100kbps,
8 bytes = 640us on-air time) may avoid some startup overflows;
it may also introduce IRQ churn. The persistent immediate
failures could instead be a latched CC1101 state or firmware
cache/build issue; only physical logs can decide. The new
boot marker proves which branch built, but does not replace
other checks.

## Validation
Pinned upstream SHA a732dd0e52c48973fad57e4950a11d8e2f2d6820,
16 ordered patches through v4.17 + isolated v4.19 patch.
No v4.18 patch, no public merge, OTA or flash by CI.

Set source:
github://smarthomewithme/wmbus-gama350-reader@experiment/v4.19-early-fifo8-irq
with refresh: always.
Expect log:
SHWM v4.19 FIFO8 ACTIVE
and
SHWM wMBus v4.19 ACTIVE

Hardware test gate: 5–10min, both meters reporting and
no overflow. If first several notifications fail with
received=0, reject v4.19 immediately and preserve v4.17
and the trusted v4.9. Don't attempt 147min before passing.
