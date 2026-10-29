# Security and privacy

This public ESPHome CC1101 / GAMA 350 Wireless M-Bus repository must never include real Wi-Fi credentials, API encryption keys, OTA passwords, fallback AP credentials, web authentication passwords, meter AES keys, private meter IDs, or raw household consumption logs.

## Safe ESPHome setup

- Store all real credentials and meter IDs in an untracked local `secrets.yaml`. The checked-in `config/secrets.example.yaml` contains **non-working placeholders and dummy identifiers**.
- Generate unique strong passwords for Wi-Fi, OTA, fallback AP and web access. Generate a unique valid 32-byte Base64 ESPHome API encryption key.
- The example web server includes authentication. Treat HTTP as local-network-only and do not port-forward it to the public Internet.
- If you use UDP forwarding, configure an endpoint you own; leave the feature disabled by default.
- Do not share your real ESPHome configuration in public issue reports.

## Raw radio logging and encryption

The v4.9 patch masks the AES key in ESPHome startup `dump_config` output as `Key: [REDACTED]`. This does not protect previously published logs, or prevent other DEBUG and `on_frame` logs from exposing raw meter telegrams, consumption data, network details or identifiers. Inspect every diagnostic snippet and redact sensitive values before sharing.

If a real secret has been disclosed anywhere, rotate or revoke it wherever feasible. Updating a README or deleting a Git-tracked file does not remove leaked values from old Git commits, copies, logs, or external conversations. Meter-specific AES key rotation may require the meter operator.

The project is a read-only hobbyist receiver, not an authoritative utility billing platform. Local law and the meter owner's authorization govern use.

Original code and patches in this repository are MIT-licensed; upstream components retain their original licenses.

Security and disclosure contact: **smarthomewithme@gmail.com**  
Project website: https://smarthomewithme.com/
