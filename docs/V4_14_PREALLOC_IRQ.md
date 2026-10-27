# SHWM CC1101 v4.14 — prepare packet before FIFO IRQ (experimental)

## Motivation

Physical v4.13 log: 27 decoded GAMA350 telegrams in ~68 minutes, 31 complete
326-byte frames, 4 3of6 errors, 325 FIFO overflow reports. Of those reports,
218 occurred with `received=0` in the current read, including frames from
other meters; 49 occurred during a 323-byte GAMA payload read. The observation
does not prove that all zero-offset overflows are GAMA or identify the cause.

## One isolated hypothesis

The previous receive task calls `std::make_unique<Packet>()` **after** the
FreeRTOS notification (FIFO threshold IRQ), before its first SPI RXBYTES sample.
Heap allocation or lock contention at this precise time could consume scarce
FIFO headroom (upstream estimates 5.12 ms to fill 64 bytes at 100 kbps).
v4.14 instead creates the packet **before** blocking on `ulTaskNotifyTake`.
This leaves the first RX read immediately after the existing IRQ notification
counter update, without altering the FIFO read policy itself.

We retain v4.9 EOF confirmation, v4.11 RXBYTES=65 treatment, v4.12 single
recovery, v4.13 post-drain polling, MDMCFG4=0x5C, FIFO threshold=0x03,
frequency 868.950 MHz, IRQ GPIO4, AGC, AES redaction and all YAML settings.
The only source-level behavior change is the allocation timing.

## Technical gates

Native regression tests; patch scope check; pinned upstream patch application;
CI source check that exactly one Packet allocation occurs *before* the IRQ
wait; ESPHome 2026.10.0 vendor/direct-GitHub compiles; Git diff check.
None can guarantee physical RX reception.

## Hardware test

Use the branch `experiment/v4.14-prealloc-irq` only once CI has passed,
keeping all other settings fixed. Start with 5–10 minutes, then extend to
60+ minutes if GAMA becomes reliable. Compare complete and decoded GAMA,
long payload overflows, zero-byte overflows (all meters), `unstable_rxbytes`,
`bursts`, `peak_fifo`, Apator and RSSI. The known physically best
reference remains v4.9; no downgrade, merge, release or OTA is performed.
