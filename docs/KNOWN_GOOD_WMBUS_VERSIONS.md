# Hardware-verified wM-Bus GAMA350 + Apator reference ledger
Updated 2026-10-28. Do not confuse historical `SHWM v4.12 RX_DIAG_1M`
log label with the actual compiled branch/firmware version.

| Version | Physical status | Duration | GAMA350 decoded/full | 3of6 errors | Overflow | Apator |
|---|---|---:|---:|---:|---:|---|
| **v4.9** | **BEST CONFIRMED DECODE RATE**, safe fallback | ~147min | **215/216 (99.54%)** | 1 | **0** | Working |
| **v4.16** | Working, lower decode rate | ~145min | 185/199 (93%) | 14 | **0** | 835 reads |
| **v4.17** | **CONFIRMED STABLE**, default development baseline | ~151.5min | **205/214 (95.79%)** | 9 | **0** | 140 reads |
| **v4.17 night** | Extended same-build stability, incomplete per-frame log | ~3h43 | 299 long radio frames total (decoded count unknown) | unknown | none observed | Working; cumulative 1364/0 payload OK/fail |
| **v4.21** | **PASS: verbatim v4.17 build/cache control** | ~162min | **188/215 (87.44%)** | 27 | **0** | 891 decoded |

Other cumulative v4.21 results: irq 1430, header_ok 1426, header_fail 4,
payload_ok 1424, payload_fail 2, queue_drops 0.
Among GAMA frames RSSI >=-74 dBm, 7/180 had a 3of6 failure;
RSSI <=-80 dBm, 20/34 had a 3of6 failure. This RF-condition imbalance
means v4.21-v4.9 decode-rate differences cannot be causally attributed
to code changes. v4.21 and v4.17 share EXACT same C/C++ radio source.

## Rejected and never to merge
- v4.12 physical test ~76min: ~448 FIFO overflows; 27/28 decoded GAMA.
- v4.18: no frames at all, recurring zero-byte FIFO overflows; changed long no-progress wait to 150us.
- v4.19: no frames at all, 635 overflows over ~164min; changed FIFO IRQ threshold 16B to 8B.
- v4.20: no frames at all, zero-byte FIFO overflows including Apator and header; changed only after-progress long waits.

Do NOT merge rejected experiments. Preserve 4.9/4.17/4.21 references.
Future diagnostic builds must derive directly from v4.17 or v4.21
and keep short-frame timing, RF values, FIFO IRQ threshold and the
3of6 decoder untouched unless a targeted physical test justifies change.
