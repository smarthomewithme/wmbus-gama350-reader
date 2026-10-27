# SHWM CC1101 v4.11: RXBYTES=65 and prefetch byte (experimental)

## Evidence, not yet an on-device fix

v4.9 commit `11b09de7f87ade632453f772c37940dbdb470c94` received 216 full
326-byte GAMA350 frames in ~147 minutes without FIFO overflows or invalid
count warnings. After the v4.10 diagnostic build was installed, the owner
observed 30 `Invalid RX FIFO count: 65` and 12 actual `RX FIFO overflow`
warnings over ~4 minutes, with no successful GAMA frames.

The **Texas Instruments CC1101 silicon errata SWRZ020E** documents a
64-byte RX FIFO **plus a one-byte SPI prefetch buffer** and RXBYTES count
of **65**, which can occur without the overflow status bit. Therefore a
stable 65 must not automatically be classified as a corrupted register
value. This resolves one source-level defect, not the proven root cause
of the physical v4.10 failure.

Source: https://www.ti.com/lit/er/swrz020e/swrz020e.pdf

## Changes from v4.10

- Treat an RXBYTES low-seven-bit count of 65 as plausible when bit 7
  (actual RX FIFO overflow) is **clear**. Reject counts above 65.
- For incomplete frames, preserve the final FIFO byte and bound each
  SPI burst to at most 64 bytes, including the 65-prefetch case.
- For a complete frame with 65 bytes still outstanding, read 64 then
  the final byte in a separate transfer.
- Keep actual overflow detection and existing receiver recovery intact.
- Keep v4.9 MARCSTATE, v4.10 five-minute diagnostic windows, RF register
  settings, ISR, scheduling, and AES/key handling unchanged.

Native tests cover every 7-bit count (0–127) and remaining frame sizes
0–512, including 64/65/66 boundaries. Both pinned upstream and
direct-from-GitHub ESPHome 2026.10.0 must compile before a hardware test.

## Safety and decision

This is an **experimental candidate**, not a production update.
No automatic OTA, merge or release. v4.9 remains the verified rollback
at `experiment/v4.9-stable-marcstate-eof`.

Do not simultaneously change the radio antenna, power supply, frequency,
SPI wiring, logger configuration or GPIOs during an A/B comparison.

After CI is green, compare the same ESP32/CC1101 board with stable v4.9
and candidate v4.11 over 10 minutes, then 60+ minutes if the initial
results are clean. Check `RX_DIAG_5M`, `Long RX`, GAMA decode counts,
water meter, overflow errors, invalid counts, and 3-of-6 errors.
Roll back immediately if v4.11 shows repeated errors or no decoded
meter frames.

If errors persist after allowing 65, investigate verified restart state
(SIDLE/SFRX/SRX), SPI signal integrity and the board's power supply
as separate experiments; do not silently treat a real overflow as a good
frame.
