# Troubleshooting ESPHome + CC1101 GAMA350 Wireless M-Bus

## Validation or build fails

1. Verify you copied the complete [ESPHome YAML](../config/wmbus-gama350.yaml), with its source pointing at `@experiment/v4.9-stable-marcstate-eof`, and put your real `secrets.yaml` in the same ESPHome directory.
2. Check every required secret exists and is correctly formatted. A 16-byte meter key is written as **32 hexadecimal characters**; ESPHome API encryption requires a new valid 32-byte Base64 key.
3. Confirm that the ESPHome build host has network access to GitHub (it downloads the pinned upstream component code).
4. Select **Clean Build Files**, then **Validate**. Use ESPHome 2026.10.1 when reproducing the documented build.
5. The example is a template, not a factory image: your Wi-Fi, keys, meter IDs, supply, hardware pinout and receive frequency must match your installation.

## Home Assistant entities are unavailable

Check ESP32 power, Wi-Fi connection, Home Assistant ESPHome API pairing, API key and any static IP you deliberately configured. A successful ESPHome build does not prove the device is powered or connected.

## Apator is detected, but GAMA 350 readings are missing

Confirm the GAMA 350 meter actually sends accessible wM-Bus telegrams, that the configured meter ID and AES key are authorized/correct, that `amiplus` is selected, and that the CC1101 antenna is suitable for 868 MHz. Examine the `RF_DIAG` and `Long RX` lines for complete **326-byte** frames. Failed 3-of-6 codes indicate a captured frame that could not be correctly decoded; this can be related to RF reception and is not a simple key-password error.

## CC1101 RX FIFO errors, 3of6 errors or intermittent signals

Maintain the tested `v4.9` radio implementation. Check supply voltage (use 3.3 V for 3.3 V-only CC1101 boards), SPI and GDO0 wiring, antenna position, local interference and RSSI first. In the physical field test, raising the receiver from the floor to a stable wall location improved RSSI by approximately 22 dB.

Do not blindly edit CC1101 FIFO/IRQ logic based on a single error. A missing nominal 30-second log window is not proof a transmitted GAMA telegram was lost.

## Optional networking features

- The public YAML uses DHCP. To use a fixed IP, uncomment `manual_ip` and enter values for your own LAN.
- UDP streaming is off by default. To use it, uncomment `socket_transmitter` and set `udp_receiver_ip` in your local secrets file.
- The built-in web server uses authentication. Keep it on a trusted local network; do not expose it directly to the Internet.
- Raw `on_frame` logging may reveal private telegrams. Remove or disable that action if you share logs publicly.

## Responsible issue reports

Provide ESPHome version, selected frequency, radio type, non-sensitive diagnostic counters and a short sanitized error excerpt. **Never publish Wi-Fi credentials, AES keys, OTA/API keys, meter IDs or household consumption logs.**

Website: https://smarthomewithme.com/  
Email: smarthomewithme@gmail.com
