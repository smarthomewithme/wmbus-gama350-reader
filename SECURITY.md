# Security and privacy

This repository accepts **no real AES meter keys, API tokens, Wi-Fi passwords, production `secrets.yaml`, or unredacted energy measurements**. `vendor/` and `config/secrets.yaml` are excluded from version control.

## AES keys in startup logs

The upstream component and public v3 source print the actual confidentiality key during `wmbus_meter::dump_config`. **Official v4 changes that field to `Key: [REDACTED]` without changing any meter keys or decryption logic.**

The patch does not remove secrets from logs previously shared or cached. Treat any older logs containing `[C][wmbus_meter:055] Key:` as sensitive. Delete/secure such logs from public locations and follow your meter provider's credential rotation process if available. **Never submit a real log of device startup without manually checking redaction**, regardless of patch version.

DEBUG logs can also print decrypted telemetry and raw meter telegrams, which can reveal consumption and meter identity. Reduce log level before public sharing and mask network identifiers (MAC, IP, SSID, BSSID).

## Safe release scope

Only original project code, patch deltas, synthetic test fixtures and documentation are published. Upstream components are cloned at a pinned revision without vendoring their source. No public release includes an ESPHome configuration with production credentials.

V4 is a read-only community diagnostic receiver. It does not issue control commands to the certified electricity meter and must not be used as an authoritative billing source.

If a secret is committed to Git history, deleting the working-tree file is insufficient: revoke/rotate when feasible and purge the affected history through an appropriate incident response process.
