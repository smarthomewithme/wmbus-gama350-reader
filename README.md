# wMBus GAMA 350 Reader (ESP32 + CC1101)

**Status: experimental candidate — no successful GAMA 350 hardware read verified yet.**

A public, reproducible project focused on getting reliable GAMA 350 electricity meter readings into Home Assistant through ESPHome. The initial hardware profile is an ESP32 DevKit (`esp32dev`) with a CC1101 at 868.950 MHz. The Apator water meter remains in the example configuration as a regression guard.

**Polski:** [README.pl.md](README.pl.md) · [Test plan](docs/TEST_PLAN.md) · [Current findings](docs/STATUS.md)

## Why this repository exists

GAMA 350 (`amiplus`, meter ID `0x12345678` (example)) produces long T1 telegrams (about 326 raw bytes), but the current device receives corrupt 3-of-6 symbols partway into the frame. The same CC1101 setup correctly receives and decrypts a shorter Apator telegram. A known-good GAMA 350 + CC1101 case has been reported upstream in [issue #420](https://github.com/SzczepanLeon/esphome-components/issues/420). A similar long-packet failure is described in [issue #453](https://github.com/SzczepanLeon/esphome-components/issues/453).

The **candidate patch** addresses three narrowly scoped issues: a C++ argument evaluation / vector buffer bug in `component.cpp`, an out-of-bounds access in `decode3of6.cpp`, and CC1101 RX FIFO last-byte handling. These changes are **not yet proven to fix GAMA 350 in real hardware**.

## Hardware (existing working wiring; do not change it)

| Signal | ESP32 |
|---|---|
| CC1101 SCK | GPIO18 |
| CC1101 MOSI | GPIO23 |
| CC1101 MISO | GPIO19 |
| CC1101 CS | GPIO15 |
| CC1101 IRQ | GPIO4 |

**Note:** The device already reads Apator. Do not try GPIO5 or other pin changes as a first step.

## Build instructions — no flashing is performed

1. Clone this repository (or download and extract the archive).
2. Prepare upstream code at the **pinned** SHA (Linux/macOS: `bash scripts/prepare_sources.sh`; Windows PowerShell: `powershell -ExecutionPolicy Bypass -File .\scripts\prepare_sources.ps1`). The command clones the upstream repository into an ignored `vendor/upstream/` folder and applies this project's narrow patch. It refuses to overwrite an existing folder.
3. Copy `config/secrets.example.yaml` to `config/secrets.yaml` and **replace all placeholders with YOUR existing secret values**. Never commit it or share the actual keys/logs. The repository contains no genuine AES keys.
4. Install ESPHome 2026.10.0 into a separate environment and run `esphome config config/wmbus-gama350.yaml` and `esphome compile config/wmbus-gama350.yaml`.
5. **Do not flash the device automatically.** Back up the actual working ESPHome configuration and existing firmware before deciding on a controlled OTA experiment.

> Caution: the example intentionally excludes optional `socket_transmitter` UDP forwarding. Preserve any existing UDP forwarding and other integrations when adapting a working device configuration.

## Native regression tests

```bash
bash scripts/test.sh
```

Runs sanitizer-backed C++ tests of 3-of-6, header CRC, memory, simulated packet lengths (53/326/430 bytes), FIFO policy and secret hygiene. No ESP32 is accessed. The GAMA fixture is a **sanitized, checksum-consistent 20-byte header derived from a genuine prefix (example ID substituted)**; full 326-byte raw frames and a full 53-byte Apator raw telegram are not available. Never misrepresent model/synthetic data as captures from the meter.

## Current scope / future roadmap

- **R1:** safe radio path, GAMA 350 + Apator baseline, repeatable test fixtures, manual hardware validation.
- **R2:** verified consecutive GAMA 350 transmissions, telemetry counters, detailed corrupt-frame diagnostics, rollback.
- **R3:** additional wMBus meters and radio modules behind tested abstractions.

## License and attribution

New scripts, test harnesses, documentation and candidate patch authored by this project: MIT (`LICENSE`). **This MIT license does not grant rights to code in `SzczepanLeon/esphome-components`.** We do not vendor their source code here. Portions of upstream `wmbus_common`/wmbusmeters are identified as GPL-3.0-or-later, while the top-level upstream repository has no recognized GitHub license file. Determine redistribution rights separately before publishing a full fork or repackaged firmware sources.

### Upstream references

- [SzczepanLeon/esphome-components](https://github.com/SzczepanLeon/esphome-components)
- [#345 CC1101 FIFO workaround](https://github.com/SzczepanLeon/esphome-components/pull/345)
- [#407 infinite length mode](https://github.com/SzczepanLeon/esphome-components/pull/407)
- [#420 GAMA 350 success](https://github.com/SzczepanLeon/esphome-components/issues/420)
- [#443/#444 earlier, different CC1101 implementation](https://github.com/SzczepanLeon/esphome-components/issues/443)
- [#453 similar long frame failures](https://github.com/SzczepanLeon/esphome-components/issues/453)