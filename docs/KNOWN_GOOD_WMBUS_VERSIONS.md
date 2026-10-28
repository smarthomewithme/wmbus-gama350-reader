# Hardware-verified reference ledger — 28 October 2026

| Version | Status | GAMA350 correct / 326B frames | Duration | FIFO overflows |
| --- | --- | ---: | ---: | ---: |
| **v4.9** | BEST decoded, safe fallback | **215/216 (99.54%)** | ~147min | 0 |
| **v4.17** | STABLE developer baseline | 205/214 (95.79%) | ~151.5min | 0 |
| **v4.21** | PASS independent clean-build control, identical C++ to v4.17 | 188/215 (87.44%) | ~162min | 0 |
| v4.16 | PASS lower decode rate | 185/199 (93%) | ~145min | 0 |

- Extended v4.17 uptime ~3h43, with cumulative payload_ok=1364,
  payload_fail=0 and 299 long radio frames (full decode count unknown).
- v4.21 Apator 891, 3of6 errors 27; weak RSSI<=-80 dBm had
  20 errors/34 frames, stronger RSSI>=-74 dBm 7/180.
  RF conditions differ; do not claim v4.21 code caused lower rate.
- REJECTED: v4.12 (448 overflows/76min); v4.18, v4.19, v4.20
  (recurrent zero-byte FIFO overflows, no meters); **v4.22**
  (confirmed MARCSTATE 0x11, zero-byte overflows, slow API connect).
- v4.22's 36s API connect vs ~3s on v4.21 is not proof of
  CPU slowdown; ESPHome versions and WiFi context changed.

Preserve tags/branches and never merge a rejected radio variant.
`SHWM v4.12 RX_DIAG_1M` is inherited diagnostics label, not
firmware identity. v4.23 is unverified diagnostic, never claim PASS
before physical test. No unattended deployment of failed variants.
