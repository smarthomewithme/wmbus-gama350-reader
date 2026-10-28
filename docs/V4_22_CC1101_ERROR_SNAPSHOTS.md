# v4.22 — CC1101 state snapshots only on failure

Based directly on physical PASS v4.21 (`a11d6f8f8efe882351796a981cbeedb73f12071a`)
which compiles the same proven v4.17 C++ radio sources.

## Scope of runtime modifications
1. In `CC1101::setup` AFTER writing config registers but BEFORE
   calibrating and entering RX, read back IOCFG0, FIFOTHR, MDMCFG4,
   PKTCTRL0 once, print `SHWM v4.22 BOOT_CONFIG`.
2. When the main RXBYTES read already indicates overflow,
   read `RXBYTES` again, `MARCSTATE`, `PKTSTATUS`, `FIFOTHR`,
   `IOCFG0` and the digital IRQ level. Log once per already-failed
   frame as `SHWM v4.22 RX_ERR`, BEFORE the existing warning and
   recovery in `Radio::receive_frame`.
3. Startup marker `SHWM wMBus v4.22 ACTIVE`.

**Zero instrumentation in the successful RX hot path**, other than
the same existing branch check. Preserves v4.17 radio config (868.950MHz,
FIFO 16B/0x03, long idle 100us, short idle 200us),
MARCSTATE EOF, 3of6, interrupts and recovery order. Readback on
boot changes setup duration slightly; it is not an identical-source
control and could shift RF startup timing. Snapshots after error
are not simultaneous with the triggering RXBYTES read. None of the
extra SPI reads ever occur after successful status read.

All 15 v4.17 upstream patches are retained byte-for-byte and in order
from v4.21, followed by patch 0016 for snapshots only.

## Expected good result
At least one GAMA350 326B and one Apator within first 2–3min,
`payload_ok > 0`, `payload_fail == 0`, no `RX_ERR` or
`SHWM v4.12 RX FIFO overflow`.
For a good receiver leave 10–15min and compare burst_count,
peak_fifo, 3of6 errors and both meters with version ledger.

## If failure repeats
Stop long test and collect **first 1–2min of logs**, including:
`SHWM v4.22 RX_ERR offset=... rx_first=... rx_second=...
marc=... pktstatus=... fifothr=... iocfg0=... irq_level=...`.
Do NOT change radio timings blindly. Retest v4.17 or v4.21
before leaving the device unattended.

No merge/release/flash from CI; next hardware step remains user-controlled.
