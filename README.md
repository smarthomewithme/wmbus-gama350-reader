# ESPHome CC1101 GAMA 350 Smart Electricity Meter Reader (Wireless M-Bus 868 MHz)

**Read a GAMA 350 / GAMA350 electricity smart meter with an ESP32 and the Texas Instruments CC1101 868 MHz radio, using ESPHome and Home Assistant.** This open-source Wireless M-Bus (wM-Bus) project also supports an Apator water meter. Receive electricity consumption (kWh), day/night tariffs, current power (W), cold-water consumption (m³), and GAMA RSSI without a cloud service.

## 📥 DOWNLOAD — TESTED & WORKING ESPHOME CONFIGURATION

### ✅ READY-TO-CUSTOMIZE ESP32 + CC1101 GAMA350 READER

**Field-tested v4.9 radio code · ESPHome 2026.10.1 build verified · Home Assistant compatible**

<a href="https://github.com/smarthomewithme/wmbus-gama350-reader/raw/refs/heads/main/config/wmbus-gama350.yaml">
  <img src="https://img.shields.io/badge/%E2%AC%87%20DOWNLOAD-TESTED%20ESPHOME%20YAML-2ea44f?style=for-the-badge" alt="Download tested and working ESPHome GAMA350 CC1101 YAML" />
</a>

### [📋 VIEW & COPY THE FULL YAML CODE](config/wmbus-gama350.yaml)

**[🔑 GET THE SECRETS TEMPLATE](config/secrets.example.yaml)**

> **Start here:** Download the complete YAML, paste it into your ESPHome device configuration, and create a local `secrets.yaml` with your own Wi-Fi details, API/OTA credentials, meter IDs and AES keys. Check the GPIO connections and the meter's radio settings before installing. **The downloadable example contains no real private credentials.** It is a field-tested, working project template—not a preconfigured firmware image for every meter.

---

[**CC1101 + GAMA350 technical guide**](docs/CC1101_GAMA350.md) · [**Troubleshooting**](docs/TROUBLESHOOTING.md)

> **Stable radio source:** This repository's public example deliberately uses `@experiment/v4.9-stable-marcstate-eof`. It is the *field-tested* firmware source. Do **not** replace that reference with `@main` just because you are reading the README on the default branch. The original verified radio commit is `11b09de7f87ade632453f772c37940dbdb470c94`. Documentation on `main` does not modify that stable branch.

## What does this ESP32 + CC1101 GAMA350 reader do?

- **GAMA 350 electricity meter:** Wireless M-Bus telegrams through the `amiplus` decoder; overall energy consumption, day tariff, night tariff, instantaneous power and received signal strength.
- **Apator water meter:** Wireless M-Bus T1 telegrams decoded through `apatorna1`; total cold-water usage in m³.
- **Home Assistant integration:** Native ESPHome API exposes each measurement as an entity.
- **CC1101 long-frame reception:** Tested with **326-byte GAMA350 RF frames** and 3-of-6 (3of6) coding. The stable v4.9 code includes FIFO/IRQ handling and bounded MARCSTATE end-of-frame confirmation.
- **ESPHome configuration you can copy:** A complete, sanitized English-language YAML with an independent `secrets.yaml` template.
- **Optional features:** Protected local web server, fallback Wi-Fi access point and opt-in UDP forwarding.

This is a **receiver**, not a control device for the electricity meter and not a certified billing instrument. A valid meter ID and its legitimately supplied decryption key are required to decode encrypted telegrams.

## Hardware: connecting CC1101 to ESP32

Use an **ESP32 DevKit / esp32dev**, a compatible **CC1101 868 MHz module and antenna**, and a suitable 3.3 V power supply.

| CC1101 connection | ESP32 DevKit pin | Purpose |
| --- | --- | --- |
| SCK / CLK | GPIO18 | SPI clock |
| MOSI / SI | GPIO23 | SPI data to CC1101 |
| MISO / SO | GPIO19 | SPI data from CC1101 |
| CS / CSN | GPIO15 | SPI chip select |
| GDO0 / IRQ | GPIO4 | Radio interrupt |
| VCC | **3.3 V only** | Module power |
| GND | GND | Common ground |

**Important:** Check the pinout and voltage requirements of your actual CC1101 board; do not apply 5 V directly to a 3.3 V-only radio module. Use an antenna designed for the 868 MHz band. A reliable supply and stable physical mounting matter.

## Quick start: install in ESPHome

1. Download [`config/wmbus-gama350.yaml`](config/wmbus-gama350.yaml), open the ESPHome Dashboard and paste its contents into your device's YAML (or use it as a new configuration). Recommended tested build environment: **ESPHome 2026.10.1**.
2. In the same ESPHome configuration directory, create `secrets.yaml` using [`config/secrets.example.yaml`](config/secrets.example.yaml) as the template. **Replace every placeholder** and dummy meter ID with your own values. Obtain your meter's AES key from the authorized provider.
3. The important `external_components` section is **already present in the full example** and should remain:

```yaml
external_components:
  - source: github://smarthomewithme/wmbus-gama350-reader@experiment/v4.9-stable-marcstate-eof
    refresh: always
    components: [wmbus_radio, wmbus_common, socket_transmitter, wmbus_meter]
```

4. Check the SPI wiring, meter types, real meter IDs, credentials, radio frequency and regional operating conditions. The supplied profile uses **868.970 MHz**, selected in a physical A/B/A trial; it is **not a universal frequency for every meter**.
5. Choose **Validate**, then **Install / Wirelessly** in ESPHome. If upgrading an older component version, use **Clean Build Files** first. Never flash over a working device without retaining its original YAML and a rollback method.
6. Add the ESPHome device to Home Assistant. The sensors appear as electricity and water measurements. The current-power source field is in kW; the example multiplies by 1000 and displays **W**.

The public example intentionally uses DHCP by default. If your network requires a static IP, uncomment the optional `manual_ip` block and enter your network's address. UDP transmission is **disabled by default**; enable the commented `socket_transmitter` block only when you own the destination server and have supplied its IP in `secrets.yaml`.

### What needs to be set in secrets.yaml?

| Setting | What the user supplies |
| --- | --- |
| `wifi_ssid`, `wifi_password` | Their own Wi-Fi connection |
| `api_encryption_key` | A newly generated 32-byte Base64 ESPHome API key |
| `ota_password` | A new unique OTA password |
| `fallback_ap_password` | A new strong fallback AP password (at least 8 characters) |
| `web_username`, `web_password` | Credentials for the local ESPHome web interface |
| `gama350_meter_id`, `apator_meter_id` | Their own meter IDs, not the example IDs |
| `gama350_aes_key`, `apator_aes_key` | Correct 16-byte meter keys written as 32 hexadecimal characters |
| `udp_receiver_ip` | Optional private UDP destination, only when forwarding is enabled |

ESPHome can generate an API encryption key in its interface; alternatively, a system with Python can generate one using `python -c "import base64,secrets;print(base64.b64encode(secrets.token_bytes(32)).decode())"`. Never copy somebody else's real secrets. An unedited example secrets file is **not ready to flash**.

## Home Assistant sensors

| Example entity description | Measurement |
| --- | --- |
| Electricity - Total Consumption | GAMA 350 accumulated kWh |
| Electricity - Day Tariff | Tariff 1 kWh |
| Electricity - Night Tariff | Tariff 2 kWh |
| Electricity - Current Power | Instantaneous W |
| Electricity - RSSI | Received GAMA signal strength in dBm |
| Water - Cold Water | Apator accumulated m³ |

ESPHome automatically derives entity IDs from the configured names; the actual IDs depend on your device and Home Assistant.

## Why CC1101 and GAMA 350 need special attention

Unlike short water-meter packets, this GAMA smart electricity meter can produce long **326-byte radio captures**. A complete raw frame may still fail `3of6` decoding when the signal is corrupted. The CC1101 receive FIFO, SPI timing, IRQ signal and RF geometry therefore matter.

This repository uses the upstream [SzczepanLeon ESPHome Wireless M-Bus components](https://github.com/SzczepanLeon/esphome-components), pinned to commit `a732dd0e52c48973fad57e4950a11d8e2f2d6820`. The loader applies eight inspectable v4.9 patches from `patches/` at build time; users do **not** need to clone or patch upstream manually.

In a controlled October 29, 2026 test with the receiver attached to a wall, both 868.950 and 868.970 MHz achieved **approximately 99% decoding success among complete 326-byte GAMA frames**. This **does not mean 99% of every broadcast was received**: a nominal 30-second slot without a logged frame is not proof that the meter transmitted and the receiver lost it. The strongest improvement came from physically repositioning the antenna/receiver, not from the 20 kHz tuning change. See [technical details](docs/CC1101_GAMA350.md).

## FAQ: GAMA350 ESPHome, CC1101 and Wireless M-Bus

**Can an ESP32 read a GAMA 350 smart meter via CC1101?** Yes, if the meter transmits compatible Wireless M-Bus frames, the radio is correctly configured and the user has the necessary authorized decryption key. Supported telegram fields can vary by meter model, firmware and setup.

**Is this a Zigbee or Wi-Fi energy meter?** No. It is an **868 MHz Wireless M-Bus RF receiver** on CC1101. The ESP32 subsequently publishes values over Wi-Fi through ESPHome to Home Assistant.

**Why does Apator work while GAMA350 fails with 3of6 errors?** Short and long frames may behave differently when RF reception is weak or the CC1101 FIFO handling is disturbed. Check RF placement and diagnostic logs before modifying firmware.

**Do I have to use 868.970 MHz?** No. It is the tested setting for one installation. Radio configuration must suit the actual meter signal and local regulations.

**How do I avoid leaking my meter key?** Put it in a local, ignored `secrets.yaml`; never paste real AES keys into GitHub issues, screenshots, sample configurations or raw debug logs. Diagnostic `on_frame` output can contain sensitive raw telegrams.

## Project maintenance, security and attribution

- **Known-good source:** [stable v4.9 branch](https://github.com/smarthomewithme/wmbus-gama350-reader/tree/experiment/v4.9-stable-marcstate-eof). Its validated radio implementation remains unchanged.
- **Build verification:** GitHub Actions compiles the public example with synthetic credentials only; no OTA, flashing or meter access.
- **Security:** Read [SECURITY.md](SECURITY.md). Web interface authentication is enabled in the example; use a trusted local network.
- **License:** Project-authored code and patches are MIT licensed. Upstream dependencies retain their respective licenses.

### Website, author and contact

Project by **Smart Home With Me**.

- Website and Home Assistant/ESPHome guides: **https://smarthomewithme.com/**
- Contact: **smarthomewithme@gmail.com**
- GitHub source: **https://github.com/smarthomewithme/wmbus-gama350-reader**

If this project helps you read your GAMA 350 smart electricity meter with CC1101 and Home Assistant, you can link to the repository or share improvements while respecting the licenses.
