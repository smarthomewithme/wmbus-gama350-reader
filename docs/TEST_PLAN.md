# Test plan: GAMA 350, CC1101, ESP32

## Desktop

1. Run bash scripts/test.sh with GCC, ASan and UBSan.
2. Run scripts/prepare_sources.sh or prepare_sources.ps1 against the pinned SHA.
3. Confirm git apply --check and git diff --check.
4. Validate the ESPHome YAML against ESPHome 2026.10.0.
5. Compile for esp32dev / ESP-IDF. Compilation is not proof of radio reception.

## Before changing the device

Preserve the existing YAML, all local secrets, any socket_transmitter/UDP forwarding and a known working firmware image. Keep the GPIO mapping unchanged. Do not upload firmware automatically.

## Hardware acceptance

- Receive at least 20 consecutive GAMA 350 telegrams.
- Verify the correct meter ID, complete 3-of-6 decode, CRC of each block and successful amiplus decryption.
- Verify that Home Assistant updates energy, both tariffs and current power when available in the telegram.
- Receive at least 20 consecutive Apator telegrams and confirm total_m3 still updates.
- Count RX FIFO overflows, timeouts and corrupt frames; investigate any error before declaring success.

## Rollback

If Apator stops updating, GAMA remains unavailable, or the device becomes unstable, restore the preserved firmware and configuration. Record the exact source SHA, results and error patterns without exposing real AES keys or meter identifiers.

The standalone FIFO model excludes SPI timing, register races, RF interference and interrupt scheduling. Actual hardware verification is mandatory.
