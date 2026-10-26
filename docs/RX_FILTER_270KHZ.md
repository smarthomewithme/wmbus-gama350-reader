# CC1101 receive filter experiment — 270.8 kHz

**Status: candidate / experimental. No successful GAMA 350 hardware test has been completed for this variant.**

## Why

The pinned upstream CC1101 driver writes `CC1101_MDMCFG4 = 0x5C`.
At 26 MHz reference oscillator, it corresponds to `CHANBW_E=1`, `CHANBW_M=1`, or **325 kHz** receiver channel bandwidth. Its old source comment incorrectly calculates approximately 203 kHz.

This experiment changes only that single register write to `0x6C`. This yields `CHANBW_E=1`, `CHANBW_M=2`, or approximately **270.833 kHz**. The lower four DRATE_E bits remain `0xC`. Modulation, data rate, deviation, sync word, frequency, AGC/AFC registers, SPI/FIFO logic, GPIO and meter drivers are unchanged.

A narrower channel filter can reject out-of-channel interference but can also reduce tolerance for frequency offset and distort valid 100 kbps 2-FSK/wM-Bus T1 packets. There is **no guarantee** of higher sensitivity or reliability. RSSI alone is not the success metric.

## Source isolation

This variant is based on clean upstream commit:

`a732dd0e52c48973fad57e4950a11d8e2f2d6820`

It **does not** include this project's separate `0001` FIFO patch, `0002` diagnostics patch or `0003` stable RXBYTES candidate.

Run on the local Home Assistant terminal, in the checked-out `experiment/cc1101-rx-bw270` branch:

```bash
cd /config/esphome/wmbus-gama350-reader
bash scripts/prepare_rx_filter_270.sh
```

The script creates a new ignored directory `vendor/rxfilter_270`; it **will not overwrite** any existing directory and does not modify YAML, the current `vendor/upstream` or firmware. No secrets are needed.

## Controlled test on an existing ESPHome instance

1. Save a copy of the **exact currently working** YAML and firmware if available, before changing anything.
2. Modify only `external_components` in the existing YAML to use the new source:

```yaml
external_components:
  - source:
      type: local
      path: /config/esphome/wmbus-gama350-reader/vendor/rxfilter_270/components
    components:
      - wmbus_radio
      - wmbus_common
      - socket_transmitter
      - wmbus_meter
```

3. Keep all remaining YAML unchanged, including pins, frequency, keys, Wi-Fi, sensor names and UDP forwarding. Run ESPHome Clean Build Files, Validate, then OTA **only after** CI build passes.
4. Leave the door in one fixed position for comparable A/B data, preferably closed. Capture at least 10 minutes for baseline and 10 minutes for the filter variant.
5. Count successful GAMA updates (`Telegram otrzymany od licznika prądu!`), non-decoded 326-byte frames, 3-of-6/CRC errors, and successful Apator updates. Do not rely on RSSI alone.

To revert: restore the saved YAML's original `external_components` source and recompile/reflash the saved firmware. No reboot alone will revert the radio register value.

**Do not upload logs containing real AES keys to a public issue/repository.**

## Scope and licensing

The incremental patch contains one register write and its documentation changes only. The upstream source is fetched without redistribution; upstream licensing and author attribution remain unchanged.

Sources:
- https://www.ti.com/lit/ds/symlink/cc1101.pdf
- https://github.com/SzczepanLeon/esphome-components
