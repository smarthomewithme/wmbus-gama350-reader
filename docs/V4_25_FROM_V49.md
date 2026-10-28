# v4.25 — selected safe backports onto winning v4.9

Direct child of physically-proven `experiment/v4.9-stable-marcstate-eof` (commit `11b09de7f87ade632453f772c37940dbdb470c94`), pinned upstream unchanged. First EIGHT original patches retained exactly, with CI-enforced git blob hashes.

**v4.9 evidence**: 45/45 GAMA350 326B in 34m, 215/216 (99.54%) in 147m, zero FIFO overflow. This is correct decodes of FULL radio frames, not of all expected 30s slots (~73–74% of expected transmissions captured). About 10 zero-byte header timeouts in 34m; many adjacent to a successful Apator read, not proven losses.

**Later 34m results**: v4.17 43/45, v4.21 43/46, v4.24 43/48 GAMA decoded, all zero FIFO overflow. Long v4.17 205/214, long v4.21 214/231. Higher success of v4.9 merits returning to it as base, but different RF conditions and durations prevent causal attribution.

### Cherry-picked only:
1. Original **v4.10 5-minute main-loop window diagnostics** with `frame_converted`, `frame_conversion_failed` counters, not new SPI/IRQ work. Preserves existing cumulative diagnostics. No logging inside high-priority receiver.
2. Original **v4.14 Packet pre-allocation before `ulTaskNotifyTake`**, reducing heap work after task wake, preserving all RX-loop code. Existing one-time startup message now identifies `SHWM v4.25 PREALLOC`. This is plausible improvement, not established as the cause of fewer header timeouts.

**NOT** imported: v4.11 RXBYTES=65 behavior (v4.9 saw none), v4.12 recovery and status path, v4.13 skip-post-progress-wait, v4.16/v4.17 shortened long-frame no-progress delay, v4.22 heavy SPI, v4.23 ISR timestamp, v4.24 marker-only (beyond startup identification). The `transceiver_cc1101.cpp` and `cc1101_fifo.h` source from v4.9 must be identical. FIFO16/868.950MHz/MARCSTATE confirmation, unconditional 200µs post-loop delay, IRQ clear, AES key redaction all unchanged.

### Acceptance gate
All four GitHub Actions must pass before OTA. Compiles under ESPHome 2026.10.1, matching current hardware. User supervision 2–3m requires BOTH GAMA350 and Apator, responsive API, zero recurring FIFO overflow; if fail revert immediately to v4.9. If PASS, 34min comparable test, then preferably 150min. Evaluate absolute GAMA decodes / expected slots, full-frame GAMA decode rate, Apator, zero-byte header timeouts, 3of6, FIFO bursts and RSSI. This is an experiment not yet physically proven. Issue #33 is the development decision record.
