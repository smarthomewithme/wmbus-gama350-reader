# v4.20 — 75µs post-progress long-frame FIFO coalescing

## Evidence, not a promised improvement

Historical v4.9 (~147min): 216 complete 326B GAMA frames / 215 decoded,
1 3of6 error, zero overflow; ~31–33 FIFO bursts per long frame.
v4.17 (~151.5min): 214 complete / 205 decoded, 9 3of6 errors,
zero FIFO overflow, 140 accepted Apator telegrams, ~57.5 bursts.
Long-frame 3of6 encoded-byte error positions varied across 9 bad frames
(175,199,90,126,93,264,3,81,276), which does not prove RF corruption
versus SPI/timing corruption. No causal conclusion from cross-run comparison.

v4.18 (150us *no-progress* long idle) and v4.19 (FIFO8 IRQ) failed on
hardware with every payload at 0 bytes, even Apator, and are
REJECTED. v4.20 is DIRECTLY based on the working v4.17,
not on those versions.

## One isolated runtime change

Add **75µs wait AFTER successful FIFO drain**, solely when
`made_progress && offset == 3 && length >= 250` (GAMA long payload).
This gives more time to accumulate bytes between two SPI drains,
hypothesized to reduce burst count from ~58 towards v4.9's ~32
without bringing back FIFO overflow. The following remain byte-for-byte
equivalent to v4.17 at runtime:
- no-progress polling: 100µs long, 200µs short/header
- all short-frame and header progress paths (no new delay)
- unstable RXBYTES 100µs retry
- hardware FIFO threshold 16B (0x03) and SPI pins/frequency/radio RF
- radio re-arm, MARCSTATE confirmation, 65B RXBYTES fix, 3of6 parser,
  early Packet allocation, queue, AES keys, logger, YAML.

The burst-count hypothesis may be wrong: **no hardware guarantee**.

## Deployment / hardware gate

16 ordered SHA-pinned upstream patches + native regression and two
ESPHome 2026.10.0 build validations. No CI flash, release, or merge.

Use `github://smarthomewithme/wmbus-gama350-reader@experiment/v4.20-long-progress-coalesce`.
Keep `refresh: always` and remaining existing YAML unchanged.
Verify boot `SHWM wMBus v4.20 ACTIVE` in UART/early startup log.

**SMOKE FIRST**: Within 2–3 minutes both GAMA and Apator must decode;
if repeated `RX FIFO overflow ... received=0` or no meter values,
immediately revert to v4.17. If smoke succeeds, evaluate 10–15min
including (a) zero FIFO overflows, (b) short Apator, (c) full GAMA,
(d) bursts/peak FIFO/3of6, and ONLY THEN 147min comparison with v4.9.
Do not change RF settings, retry logic, OTA, or wiring during test.
