# Offline binary forensics — v4.9 success vs v4.25a and v4.25 failures

## Decision & physical proof
- **v4.9 is frozen**: original branch `experiment/v4.9-stable-marcstate-eof`,
  pinned commit `11b09de7f87ade632453f772c37940dbdb470c94`.
  Long radio test: 215/216 fully captured GAMA350 frames decoded, 0 FIFO overflow;
  short return-to-baseline test on ESPHome 2026.10.1: 11/11 GAMA350 and 43 Apator
  in ~8 min, zero overflow and zero rejected RXBYTES=65.
- **v4.25a** had only v4.10 main-loop diagnostics added to v4.9, but physical
  reception failed: 9 rejected RXBYTES=65, 6 FIFO overflows and 0 meter
  telegrams in ~2 min. No v4.14 packet preallocation in this build.
- **v4.25** combined v4.10 diagnostics + v4.14 preallocation: 5 rejected
  RXBYTES=65 and 2 overflows in ~1 min, no meter decodes.
- **v4.24** only added a startup log string to v4.21 and passed ~34min;
  this does not establish byte-layout harmlessness for all code changes.

## What this changes
**No runtime firmware modifications.** Adds one read-only workflow and one
analysis script to a branch built from exact known-good v4.9.

Pinned ESPHome **2026.10.1**, three exact source commits and verified GitHub
branch refs, same YAML and deterministic dummy credentials. Compiles all three,
then verifies component-source scope and byte-identical CC1101 FIFO driver.
Reads compiled ELF, DWARF class sizes/offsets (if present), Xtensa function symbol
sizes and ELF memory sections. Compares exact source diffs.

Only a **text** report is uploaded; never firmware, private API keys or maps.
No flash, no Home Assistant access, no publishing, no merge. If relevant
toolchain symbols/DWARF are unavailable, the report explicitly says so.

## What to infer and what not to infer
An altered `Radio` object size/layout and generated code addresses are
candidates, not proven root causes. The v4.10 diagnostic report fires only
after 300,000ms, long after the first overflow; the added conversion counters
run after queued packet conversion, whereas the failure seems to be before
successful packet reception. This favors investigating memory placement/task
scheduling/IRQ-to-SPI delays over modifying the CC1101 decoder blindly.

Before considering any further OTA test, inspect and interpret this report,
then design a *single*, measurable change with a direct falsifiable hypothesis
and a rollback gate. Leave the working device on v4.9 throughout.
See issue #33 and physical-failed PRs #34/#35.
