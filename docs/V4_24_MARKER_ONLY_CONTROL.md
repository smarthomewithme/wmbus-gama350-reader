# v4.24 — Minimal marker-only firmware layout control

Hardware **PASS**: v4.21 on ESPHome 2026.10.1 for ~165min,
214/231 GAMA350 frames decoded, 883 Apator, zero FIFO overflow.
Hardware **FAIL**: v4.22 and v4.23 on same ESPHome 2026.10.1,
zero-byte CC1101 overflow before reading packet headers.

CI comparison `diagnostics/v421-v423-build-compare`:
4.21 and 4.23 both compiled PASS under identical ESPHome 2026.10.1.
Exactly one prepared runtime source file differed:
`wmbus_radio/component.cpp`. ELF sizes 21634148 vs 21642108B
(+7960B). The ELF hash difference is not causal proof.

### What this test changes

Only APPENDS `[SHWM v4.24 MARKER_ONLY]` to one **existing**
`ESP_LOGI(... "SHWM wMBus v4.17 ACTIVE...")` startup
string. Same number/position of logging calls, no additional radio
register reads, no ISR/IRQ/timing/priority/task/source changes,
no new function calls. All 15 original good v4.17 patches retained
with matching git blob hashes; one patch modifies exactly ONE C++
string literal. It creates a different build/data layout but does
not intentionally alter receiver behavior.

This is a *control*, not an improvement or guarantee of identical
compiled instruction layout or initial timing: changed string
length or object placement may indirectly affect the binary.

### Test protocol — ONLY after 4 CI green
1. ESPHome 2026.10.1, same YAML, no changes to wiring/network.
   Set source `github://smarthomewithme/wmbus-gama350-reader@experiment/v4.24-marker-only-control`,
   refresh always, Clean Build Files.
2. After OTA supervised 2–3 minute smoke: both Apator and GAMA350
   decoded; `payload_fail=0`, no repeated FIFO overflow, responsive API.
   Check startup marker includes `[SHWM v4.24 MARKER_ONLY]`.
3. FAIL → collect 1–2 minute log and immediately restore v4.21.
   A marker-only failure suggests build/layout/startup sensitivity,
   **not proof** of specific memory mechanism.
4. PASS → retain v4.21 as proven stable and next isolate one
   v4.23 instrumentation group at a time (main-loop / task / ISR).
   Do not combine changes in one experimental build.

CI never flashes or reads user's actual secrets. No merge/release.
