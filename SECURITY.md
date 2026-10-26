# Security and privacy

This repository accepts **no real user AES keys, API tokens, passwords, production `secrets.yaml`, or unredacted personal energy measurements**.

`config/secrets.yaml` and `vendor/` are ignored by Git. Do not change those rules before publishing. If a credential is accidentally exposed, rotate it outside this repository and remove it from Git history; deleting the file in a subsequent commit is not enough.

The project is a development candidate, not a certified or safety-critical utility billing system. Never issue commands to alter the official meter; the project reads wireless broadcasts only.