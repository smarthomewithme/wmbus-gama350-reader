# wM-Bus GAMA350 + Apator for ESPHome

**Field-tested stable v4.9 receiver (ESP32 + CC1101).** Tested with ESPHome 2026.10.1 on October 29, 2026. The radio firmware uses the validated, frozen eight-patch v4.9 implementation. Supports GAMA350 (`amiplus`) and Apator (`apatorna1`).

## Install

Use this in your existing ESPHome YAML:

```yaml
external_components:
  - source: github://smarthomewithme/wmbus-gama350-reader@main
    components: [wmbus_radio, wmbus_common, wmbus_meter, socket_transmitter]
```

The tested installation uses `frequency: 868.970MHz` under `wmbus_radio`, but your installation may require another frequency. Preserve your existing GPIO pins, device settings and secrets. Back up your working YAML and firmware before OTA. If changing component versions, use **Clean Build Files** before validation.

[Sanitized example YAML](config/wmbus-gama350.yaml) · [Example secrets](config/secrets.example.yaml) · [Polski](README.pl.md)

**Never publish production `secrets.yaml`.** The sample files contain placeholders, not the private device configuration.

## Provenance

- Hardware-tested v4.9 receiver commit: `11b09de7f87ade632453f772c37940dbdb470c94`.
- Upstream: [SzczepanLeon/esphome-components](https://github.com/SzczepanLeon/esphome-components), pinned at `a732dd0e52c48973fad57e4950a11d8e2f2d6820`.
- The component bootstrap fetches that upstream source and applies precisely `patches/0001–0008`. Manual cloning is not required for ordinary ESPHome installs.
- CI tests guard the code, but RF reception still requires physical validation.

## Evidence and limitations

With the receiver secured on a wall, both 868.950 and 868.970 MHz yielded approximately 99% success **among complete 326-byte GAMA frames received**. This is not a measure of all transmitted messages: silent nominal 30-second slots cannot be declared packet loss without a second independent receiver. 868.970 MHz was chosen for continued use, but a meaningful decode-success advantage over 868.950 MHz was not established.

## Security and license

Do not publish real Wi-Fi/API/OTA/AES secrets, meter IDs, or raw household measurement logs. This version masks the AES key in startup configuration logs, but DEBUG output may still contain private measurements. Repository-authored glue and patches are MIT; original upstream dependencies retain their own licenses. See [SECURITY.md](SECURITY.md) and [LICENSE](LICENSE).

This is a community read-only receiver, not a billing-certified utility meter.
