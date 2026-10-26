# wMBus GAMA 350 Reader for ESPHome

ESP32 + CC1101 · Home Assistant · GAMA 350 (`amiplus`) · Apator (`apatorna1`)

**Official public v4 diagnostic source. Installs directly from GitHub in ESPHome — no terminal, clone, patches or local paths required.**

[Instrukcja po polsku](README.pl.md) · [Diagnostics and rollback](docs/V4_DIAGNOSTICS.md) · [Upstream project](https://github.com/SzczepanLeon/esphome-components)

## 1. Install in ESPHome (recommended)

Open your existing ESPHome device YAML and **replace its current `external_components` entry** with:

```yaml
external_components:
  - source: github://smarthomewithme/wmbus-gama350-reader@main
    components: [wmbus_radio, wmbus_common, wmbus_meter, socket_transmitter]
```

Save → Validate → Install → Wirelessly. If previously using a different version of these components, perform **Clean Build Files** before installing.

**Do not copy the example YAML over your device.** Keep your existing ESP32 pins, radio frequency, Wi-Fi/API/OTA configuration, meter IDs, AES keys, sensors and any UDP forwarding exactly as they were. Preserve a copy of the previously working YAML and firmware for rollback.

A working ESPHome 2026.10.0 installation with GitHub access is required. The first validation may take longer because the build system downloads the upstream component source automatically. There is no terminal command for the user.

## 2. What makes this possible?

The public repository hosts four small ESPHome component entrypoints in `components/` and a pinned-source bootstrap loader. During the first validation on the ESPHome build host, the loader:

1. Downloads [SzczepanLeon's original component repository](https://github.com/SzczepanLeon/esphome-components) at SHA `a732dd0e52c48973fad57e4950a11d8e2f2d6820`.
2. Applies four inspectable local patch files from this repository.
3. Verifies the unchanged 325 kHz CC1101 receiver filter and redacted AES config logs.
4. Makes the downloaded components available to ESPHome for compilation.

**All these steps run automatically inside ESPHome.** The source pin guards against upstream changes, and there are no additional repositories or installers to configure in YAML. Unlike shipping a full fork, this project does not redistribute the original upstream files or the GPL-covered `wmbusmeters` implementation.

## 3. Real hardware evidence

The previous v3 code ran on a physical ESP32 in October 2026 with the garage door closed. In approximately 30 minutes it decoded 39 GAMA frames (out of ~60 transmissions expected at the observed 30-second rate), received 41 complete GAMA radio frames including two 3-of-6 errors, and decoded 161 Apator water meter telegrams. It therefore **works, but misses some GAMA transmissions**.

The v4 release retains v3 CC1101 radio configuration and adds diagnostic counters / modem snapshots, plus masks the AES key on boot. Its reception reliability **has not yet been measured on physical hardware**. A successful ESPHome CI build does not prove 100% reception.

## 4. V4 diagnostics

- Every five minutes: `RX_DIAG cumulative` counts the radio FIFO interrupt notifications, successful/failed headers and payload reads, long packets, and queue drops.
- For complete long packets: `RF_DIAG` records `freqest_raw`, `lqi_raw`, `marcstate`.
- Existing logs: `Long RX`, `unstable_rxbytes`, `Long frame 3of6 error`.
- ESPHome startup config: `Key: [REDACTED]` instead of printing real meter AES secrets.

A GPIO4/FIFO interrupt is **not** the same as a decoded meter telegram; the counters are diagnostic, not a transmission guarantee.

## 5. Security and licensing

No production keys or identifiable real telegram logs are committed. Older firmwares (including original upstream and v3) can print unredacted AES keys at boot. V4 masks that field but DEBUG logs may still contain private decrypted meter measurements. Redact before posting publicly.

Original project glue and patches are MIT-licensed. The bootstrap fetches upstream sources separately and preserves their attribution and applicable licenses. Third-party upstream code is **not** relicensed by the repository's MIT license. See [SECURITY.md](SECURITY.md).

### Developer-only manual build

Developers who want a reproducible local tree can still run `bash scripts/prepare_cc1101_v4.sh`, but **this is not necessary for normal ESPHome installation**.

This is a community read-only receiver, not a utility billing-certified device.
