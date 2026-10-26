# wMBus GAMA 350 Reader — ESP32 + CC1101

**Official public source repository · v4 diagnostic candidate (hardware validation pending).**

**Polski:** [README.pl.md](README.pl.md) · [v4 upgrade and rollback](docs/V4_DIAGNOSTICS.md) · [tests](docs/TEST_PLAN.md)

This repository maintains reproducible, inspectable patches for the CC1101 wM-Bus receiver on ESPHome. It reads GAMA 350 electricity meter T1 telegrams through the existing upstream `amiplus` decoder and preserves Apator `apatorna1` reception.

## Verified hardware results and honest limits

- **v3 hardware-tested, 26 Oct 2026:** 39 successfully decoded GAMA telegrams in roughly 30 minutes (around 65% of 60 expected 30-second transmissions); 41 complete 326-byte frames, with two 3-of-6 errors. 161 Apator messages decoded correctly. 2 RX FIFO overflows were logged. Gateway/door remained shut during the sample.
- Complete GAMA frames that made it through the receive pipeline decoded at 39/41 (95%). This does **not** establish 95% end-to-end reception or demonstrate that v3 outperforms another version under identical RF conditions.
- **v4 is an observational update built on v3**: periodic receiver-stage counters, post-frame modem status snapshots, and safe AES startup log redaction. The 325 kHz CC1101 receive filter, GPIO wiring, frequency, and meter drivers are unchanged. Physical v4 reception has **not yet been measured**.
- Radio conditions can still cause missed broadcasts. The GPIO4 interrupt indicates an RX FIFO threshold, not a guaranteed sync event or a missed GAMA transmission. No firmware can guarantee reliable reception through a heavily attenuating path.

## Install sources (safe and reproducible)

The project intentionally **does not commit or relicense upstream files**. It checks out the exact upstream revision and applies four inspectable patches in a separate ignored directory:

```bash
git clone https://github.com/smarthomewithme/wmbus-gama350-reader.git
cd wmbus-gama350-reader
bash scripts/prepare_cc1101_v4.sh
```

This creates `vendor/cc1101_v4/components` without overwriting `vendor/upstream`, `vendor/cc1101_v3`, configuration or firmware. If the target folder exists, the script refuses to modify it.

Configure your **existing** ESPHome node's `external_components` to use that directory, keeping your own pins, Wi-Fi, AES keys, meter IDs, automations and UDP forwarding. Example for a repo installed under `/config/esphome/wmbus-gama350-reader`:

```yaml
external_components:
  - source:
      type: local
      path: /config/esphome/wmbus-gama350-reader/vendor/cc1101_v4/components
    components: [wmbus_radio, wmbus_common, wmbus_meter, socket_transmitter]
```

**Do not replace a working YAML with the repository's demonstration config.** Back up the existing YAML and firmware. Run ESPHome Clean Build Files, Validate and a local Compile before considering OTA. There is **no automatic flashing**.

Full instructions, expected diagnostics and rollback: [docs/V4_DIAGNOSTICS.md](docs/V4_DIAGNOSTICS.md).

## Hardware profile used for field test

| CC1101 signal | ESP32 DevKit |
|---|---|
| SCK | GPIO18 |
| MOSI | GPIO23 |
| MISO | GPIO19 |
| CS | GPIO15 |
| IRQ / GDO0 | GPIO4 |

Radio 868.950 MHz; ESPHome 2026.10.0; CC1101 `MDMCFG4=0x5C` (325 kHz). These are field-tested settings, **not universal wiring instructions**.

## Changes from upstream

- `0001`: packet buffer/decode boundary safety, CC1101 FIFO last-byte handling.
- `0002`: long-frame 3-of-6 and FIFO burst diagnostics.
- `0003`: bounded stable `RXBYTES` polling to avoid trusting single asynchronous readings.
- `0004`: cumulative `RX_DIAG` telemetry, `RF_DIAG` modem snapshots after successful radio reception, and redacted AES key display during ESPHome startup.

Run regression tests using `bash scripts/test.sh`. An independent [GitHub Actions workflow](.github/workflows/official-v4.yml) validates all patches and compiles a synthetic-secret ESPHome firmware. The workflows never contact or flash a physical ESP32.

## Security and licensing

Never paste real AES keys, `secrets.yaml`, MQTT/API credentials or unredacted meter telegrams into public issues or commits. **Earlier upstream and v3 firmwares print the meter AES key in the boot log**; v4 redacts that startup field. Already shared logs remain sensitive and must be handled separately. Other logging of decrypted telegrams is enabled by DEBUG and may reveal consumption.

Original project files and incremental patches are MIT under [LICENSE](LICENSE). The third-party upstream source is fetched separately from [SzczepanLeon/esphome-components](https://github.com/SzczepanLeon/esphome-components). This license does not grant redistribution rights to upstream code or third-party components (some include GPL notices). No prebuilt firmware containing third-party code is distributed here.

This is a community-developed read-only diagnostic integration, not a billing-certified electricity meter replacement.
