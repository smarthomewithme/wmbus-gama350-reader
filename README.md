# SHWM wMBus GAMA350 / Apator — stable v4.9 + passive diagnostics v4.27

ESP32 + CC1101, ESPHome, Home Assistant. **Physical receiver baseline is frozen at v4.9**. The new **v4.27** is a **host-side diagnostic toolkit**, not a rewritten RF receiver. It identifies 326-byte GAMA frames, early and late 3of6 errors, nominal 30-second windows without observed full packets, and Apator/IRQ correlations.

## Proven radio firmware (do not change a working device)

```yaml
external_components:
  - source: github://smarthomewithme/wmbus-gama350-reader@experiment/v4.9-stable-marcstate-eof
    refresh: always
    components: [wmbus_radio, wmbus_common, wmbus_meter, socket_transmitter]
```

Keep your own YAML settings, keys and meter IDs. Do **not** use `@main` as a presumed v4.9 replacement. v4.9 is separately verified in physical reception: 215/216 complete GAMA frames decoded over ~147 minutes, 0 FIFO overflows, and Apator data. These statistics are *conditional on full 326B frame receipt*, not a count of all meter transmissions.

## v4.27 offline observer — requires no reflash

1. Export text logs from the **unchanged v4.9 ESPHome device** with existing CC1101 DEBUG logs.
2. Download/run [scripts/analyze_v427.py](scripts/analyze_v427.py) locally with Python 3.10+:

```powershell
py -3 scripts\analyze_v427.py --input "C:\Users\Public\gama-log.txt" --out "C:\Users\Public\gama-report"
```

The tool writes `report.md`, `summary.json`, `gama_slots.csv`, `errors_3of6.csv`. Use multiple `--input` flags for overlapping logs: the analyzer deduplicates them. Reports contain only timings and non-secret diagnostic metrics, not the raw private log or AES keys.

Read [the Polish diagnostic procedure](docs/V427_PASSIVE_DIAGNOSTICS.md) and [the GitHub PR](https://github.com/smarthomewithme/wmbus-gama350-reader/pull/38).

**A missing nominal time slot is not proof the meter transmitted or the receiver failed.** To prove missed RF synchronization requires an independent second receiver or SDR. A 3of6 byte position plus LQI(raw)/RSSI correlation does not establish the root cause.

## Repository cleanup

The owner retired 34 historical experiment/diagnostic/release branches in October 2026, with 29 old pull requests closed, leaving only `main`, immutable known-good `experiment/v4.9-stable-marcstate-eof`, and this `diagnostics/v4.27-v49-passive-observer` branch. The exact old Git SHAs are in [the legacy archive](docs/LEGACY_REF_ARCHIVE_20261028.json) if historical reconstruction is needed.

Upstream component by [SzczepanLeon](https://github.com/SzczepanLeon/esphome-components), pinned source with original license and attribution. Do not publish private logs or AES keys. This project is not a billing-certified meter.
