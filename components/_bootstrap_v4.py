"""Install pinned upstream components on first ESPHome import.

All source is retrieved on the user's ESPHome build host, never redistributed
through this repository. This bootstrap is intentionally limited to the exact
upstream commit and four reviewed patch files in this project.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from filelock import FileLock

_LOGGER = logging.getLogger("esphome.components.shwm_wmbus")
_UPSTREAM = "https://github.com/SzczepanLeon/esphome-components.git"
_COMMIT = "a732dd0e52c48973fad57e4950a11d8e2f2d6820"
_COMPONENTS = ("wmbus_common", "wmbus_radio", "wmbus_meter", "socket_transmitter")
_PATCHES = (
    "0001-safe-packet-decoder-and-cc1101-fifo.patch",
    "0002-cc1101-long-frame-diagnostics.patch",
    "0003-cc1101-stable-rxbytes.patch",
    "0004-radio-diagnostics-and-key-redaction.patch",
)


def _run(args: list[str], *, cwd: Path | None = None) -> str:
    # An ESPHome container may be launched inside another Git checkout.
    # Prevent inherited GIT_DIR etc. from redirecting Git to a different repo.
    env = {k: v for k, v in os.environ.items()
           if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE",
                        "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
                        "GIT_COMMON_DIR", "GIT_NAMESPACE")}
    result = subprocess.run(
        args, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=180, env=env, check=False,
    )
    if result.returncode != 0:
        excerpt = result.stderr[-1200:].strip() or "Unknown Git error"
        raise RuntimeError(f"wMBus v4 source preparation failed: {excerpt}")
    return result.stdout.strip()


def ensure_v4_components(repo_root: Path) -> None:
    repo_root = repo_root.resolve()
    components_root = repo_root / "components"
    marker = components_root / ".shwm_v4_ready"
    lock = FileLock(str(repo_root / ".shwm_v4_install.lock"), timeout=240)

    with lock:
        if marker.is_file() and marker.read_text(encoding="ascii").strip() == _COMMIT:
            if all((components_root / name / "__init__.py").is_file()
                   for name in _COMPONENTS):
                return

        patches_dir = repo_root / "patches"
        missing = [p for p in _PATCHES if not (patches_dir / p).is_file()]
        if missing:
            raise RuntimeError("Required v4 patch files missing: " + ", ".join(missing))

        _LOGGER.info("Preparing CC1101 v4 sources from pinned upstream revision.")
        with tempfile.TemporaryDirectory(prefix="shwm-wmbus-v4-") as temporary:
            checkout = Path(temporary) / "upstream"
            _run(["git", "clone", "--quiet", _UPSTREAM, str(checkout)])
            _run(["git", "checkout", "--quiet", "--detach", _COMMIT], cwd=checkout)
            if _run(["git", "rev-parse", "HEAD"], cwd=checkout) != _COMMIT:
                raise RuntimeError("wMBus v4 upstream commit SHA did not match")

            for name in _PATCHES:
                patch = str(patches_dir / name)
                _run(["git", "apply", "--check", patch], cwd=checkout)
                _run(["git", "apply", patch], cwd=checkout)
            _run(["git", "diff", "--check"], cwd=checkout)

            radio = (checkout / "components/wmbus_radio/transceiver_cc1101.cpp")
            meter = (checkout / "components/wmbus_meter/wmbus_meter.cpp")
            text = radio.read_text(encoding="utf-8")
            secret_text = meter.read_text(encoding="utf-8")
            if ('this->write_register(CC1101_MDMCFG4, 0x5C);' not in text or
                    'this->write_register(CC1101_MDMCFG4, 0x6C);' in text or
                    "RX_DIAG" not in
                    (checkout / "components/wmbus_radio/component.cpp").read_text(encoding="utf-8") or
                    "Key: [REDACTED]" not in secret_text or
                    "Key: %s" in secret_text):
                raise RuntimeError("wMBus v4 verification failed")

            # Build the full package tree before making the ready marker visible.
            # Include the original files and license notices unchanged.
            for name in _COMPONENTS:
                source = checkout / "components" / name
                if not (source / "__init__.py").is_file():
                    raise RuntimeError(f"Upstream component {name} is missing")
                shutil.copytree(source, components_root / name, dirs_exist_ok=True)

        marker.write_text(_COMMIT + "\n", encoding="ascii")
        _LOGGER.info("CC1101 v4 components ready; AES startup keys redacted.")
