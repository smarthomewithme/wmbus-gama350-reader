# v4.25a experimental control: v4.9 + only v4.10 diagnostics

**Reason:** physical v4.25 combining two backports failed immediately on 2026-10-28 at 15:24: 5 cases of CC1101 RXBYTES=65 rejected by original v4.9 FIFO validation, 2 hardware FIFO overflows, no successful meter telegrams in first minute. PR #34 records this physical failure. CI 4/4 green was NOT a radio validation.

This branch is an **unmerged** isolated experiment directly from known-good v4.9 SHA `11b09de7f87ade632453f772c37940dbdb470c94` — all 8 original v4.9 patches preserved with verified git-blob hashes. Exactly one v4.10 patch was added verbatim: 5-minute main-loop diagnostics and conversion counters. It does not add Packet preallocation and does NOT change transceiver_cc1101.cpp, cc1101_fifo.h, IRQ, FIFO16 threshold, MARCSTATE confirmation or unconditional 200µs polling.

**CRITICAL FIRST GATE:** The original 147-minute v4.9 result was on ESPHome 2026.10.0. Before testing this branch, **flash exact unmodified v4.9 on current 2026.10.1** using the same YAML, Clean Build Files and observe BOTH meters and 0 overflow for 2–3min (preferably more). If the baseline fails, do not flash this experiment; investigate toolchain or device/boot/power state first.

If v4.9+2026.10.1 passes, test v4.25a with Clean Build Files, then compare 34m of the same metrics: successful GAMA350 326B frame decodes per full frames and per nominal slots, Apator decodes, RXBYTES=65, true hardware FIFO overflow, header timeout rate, FIFO bursts and RSSI.

Do NOT blindly accept reported RXBYTES=65 or add SPI readbacks in high-priority task. The legitimate 65-prefetch CC1101 erratum is a hypothesis that needs a distinct controlled test after stability of the v4.9 reference is re-established. No OTA from CI, no merge/release.
