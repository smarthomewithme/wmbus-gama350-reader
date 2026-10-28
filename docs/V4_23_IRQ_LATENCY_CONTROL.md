# v4.23 IRQ-to-task latency control (NO extra CC1101 SPI)

Physical evidence: v4.21 (~162 min) received both meters with zero
FIFO overflow. v4.22 (2026-10-28 10:08) slowed API connection to
36.17s versus v4.21 3.4s (different ESPHome build versions;
correlation only), decoded no meters and gave persistent hardware
RXFIFO_OVERFLOW (MARCSTATE 0x11, RXBYTES 0xBE/0xC1,
FIFOTHR=0x03, IOCFG0=0x40, IRQ=LOW).
v4.22 read multiple CC1101 SPI status/config registers and logged
long warning lines from radio_recv priority 24 on every overflow.
This expensive instrumentation is REJECTED, as are v4.18–v4.20.

Direct base: working v4.21, exact v4.17 RF/timing/3of6 code, plus:
- ESP-IDF `esp_timer_get_time()` 32-bit truncated microsecond timestamp
  stored by original IRQ callback; no SPI or logging in ISR.
- In receive_frame after task wakes, measure age of the most recent
  IRQ when notification count=1. Track latest & max; report count of
  coalesced additional notifications when notification count>1.
- Once a minute in *main loop*, log
  `SHWM v4.23 IRQ_LATENCY last_us=... max_us=... coalesced=...`.
- The latest IRQ timestamp can underestimate latency when multiple
  edges occur; coalesced notification count flags but cannot fully
  eliminate that ambiguity.
- Zero additional CC1101 register reads, zero added log calls in
  ISR / high-priority receiver. ISR code slightly longer than v4.21;
  this is a diagnostic control, not claimed identical performance.
- Existing v4.12 overflow WARN remains as baseline; no changing
  RX task priority, 16B threshold, retry pacing, MARCSTATE,
  decode3of6, frequency or modem settings.

This is NOT a demonstrated runtime fix. C/C++ firmware changes
could still cause zero-byte overflows. Consider restoring v4.21
immediately to regain reliable operation.

After all 4 CI PASS, clean-build and supervised 2–3min smoke.
Need Apator and GAMA decode. If any repeated zero-byte overflow,
capture the first 1–2min including the IRQ_LATENCY and existing
RX_DIAG summary, then revert to v4.21. If smoke passes, leave
10–15min and compare max_us against known time from 16B to full
64B FIFO (~3.84ms at 100kbps, ignoring framing nuances).
Do not infer CPU bottleneck solely from long ESPHome API connection,
which includes network state. When comparing firmware, pin ESPHome
2026.10.0 versus 2026.10.1 to isolate build-version effects.
