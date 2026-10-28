# v4.27 Diagnostic — **receiver binary source exactly as v4.9**

## Purpose

Find patterns associated with **unobserved GAMA350 broadcasts** and **3of6 corruption** without risking the v4.25a memory/layout regression. The v4.9 components, all 8 patches, pinned upstream, YAML, SPI, IRQ, polling and FreeRTOS code are completely **unchanged** on this branch (enforced by CI comparing to exact v4.9 SHA `11b09de7f87ade632453f772c37940dbdb470c94`).

**Important:** v4.27 is an **external observation bundle, not new RF firmware**. Using its `external_components` should compile the same receiver as v4.9. You do not need to reflash: the original working v4.9 device already emits these logs at `CC1101: DEBUG`. This avoids needless OTA risk.

## Evidence available

- For each 326-byte `Long RX`: timestamp, bursts, FIFO peak, duration, RSSI, unstable reads, matching `RF_DIAG` freqest/lqi/marcstate (raw).
- Pair following `Long frame 3of6 error` with its full frame and show encoded byte/symbol, RSSI and raw RF indicators.
- Pair successful `Telegram otrzymany od licznika prądu!` with full frames; show conditional FULL-frame decode percentage, distinct from estimated broadcast coverage.
- Infer **30-second expected GAMA slots** and list any without a **logged complete 326B frame**. A missing slot is *NOT proof* the meter transmitted or that the receiver's RF stage failed. If sync was never detected, user-space logs cannot reconstruct the missed radio waveform.
- Apator packet count / median interval / candidate switch to ~60-second cadence; header timeout, FIFO overflow, RXBYTES65, and cumulative IRQ snapshot.
- Optional association with water or header timeout near a slot is correlation, not collision proof.

## Windows usage

Keep v4.9 on the device and collect/export ESPHome logs as ordinary text using the dashboard (or existing log collection). Run with Python 3.10+ on the exported file (repeat `--input` for overlapping logs):

```powershell
py -3 scripts\analyze_v427.py --input "C:\Users\Public\gama-log.txt" --out "C:\Users\Public\gama-report"
```

Generated files: `report.md`, `summary.json`, `gama_slots.csv` and `errors_3of6.csv`. No raw packet data, meter IDs, Wi-Fi identifiers, secrets or decrypted readings are written in the report. Raw user-provided log stays local.

### If you want to explicitly select this branch in ESPHome

```yaml
external_components:
  - source: github://smarthomewithme/wmbus-gama350-reader@diagnostics/v4.27-v49-passive-observer
    refresh: always
    components:
      - wmbus_radio
      - wmbus_common
      - wmbus_meter
      - socket_transmitter
```

There is **no benefit in flashing** the branch when v4.9 already works. Do not adjust logs to VERBOSE, do not enable direct ISR logging, and do not disclose real meter IDs/AES keys.

## Safety and follow-up

- The 2026-10-28 193-minute v4.26 experiment reported 266/274 decoded full GAMA frames (8 x 3of6) and 984 Apator, 0 overflow; the v4.9 earlier 147-minute baseline was 215/216 (1 x 3of6), 850 Apator. Different times/conditions; not evidence of a specific cause.
- Initial questions: missing slots correlated with water intervals or Wi-Fi scans? Are errors at encoded bytes 3/5/9 associated with anomalous LQI(raw) vs nearby valid frames? Is there a periodic phase of missed GAMA slots?
- This tooling alone **cannot measure RSSI at an undetected transmission**, distinguish silence vs failure-to-sync, nor confirm that the source meter emitted each expected packet.
- For true RF-level diagnosis, a second independent receiver / SDR capture in 868MHz band with synchronized timestamps would be required; it must remain read-only and comply with local spectrum rules.
- No OTA, merge, release or deletion of v4.9.
