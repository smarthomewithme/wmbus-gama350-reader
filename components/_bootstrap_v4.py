"""Build pinned CC1101 v4 sources inside the ESPHome GitHub component cache.

The published __init__.py entrypoints MUST remain tracked bootstrap shims.
GitHub refresh restores tracked files, so upstream initializers live in a
separate, ignored cache and are executed by the shims without overwriting them.
"""
from __future__ import annotations

import hashlib
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
    "0005-experimental-fifo16-threshold.patch",
    "0006-v4_4-clear-stale-irq.patch",
    "0007-v4_5-initialize-isr-woken.patch",
    "0008-v4_8-bounded-invalid-rxbytes-recheck.patch",
)
_CACHE_LAYOUT = b"shwm-wmbus-v4.8-bounded-rxbytes-recheck-v1\n"
_SHIM_SENTINEL = "_shwm_wmbus_v4_bootstrap"


def _run(args: list[str], *, cwd: Path | None = None) -> str:
    # Avoid inheriting a different repository's Git environment from ESPHome.
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


def _fingerprint(repo_root: Path) -> str:
    digest = hashlib.sha256()
    digest.update(_CACHE_LAYOUT)
    digest.update(_COMMIT.encode("ascii"))
    for name in _PATCHES:
        patch = repo_root / "patches" / name
        if not patch.is_file():
            raise RuntimeError(f"Missing required CC1101 patch: {name}")
        digest.update(name.encode("ascii"))
        digest.update(patch.read_bytes())
    return digest.hexdigest()


def _ready(components_root: Path, cache_root: Path, fingerprint: str) -> bool:
    manifest = cache_root / "manifest.sha256"
    if not manifest.is_file():
        return False
    if manifest.read_text(encoding="ascii").strip() != fingerprint:
        return False
    for name in _COMPONENTS:
        stub = components_root / name / "__init__.py"
        upstream_initializer = cache_root / name / "__init__.py"
        if not stub.is_file() or not upstream_initializer.is_file():
            return False
        if _SHIM_SENTINEL not in stub.read_text(encoding="utf-8"):
            return False
        if _SHIM_SENTINEL in upstream_initializer.read_text(encoding="utf-8"):
            return False
    radio = components_root / "wmbus_radio" / "transceiver_cc1101.cpp"
    fifo = components_root / "wmbus_radio" / "cc1101_fifo.h"
    meter = components_root / "wmbus_meter" / "wmbus_meter.cpp"
    component = components_root / "wmbus_radio" / "component.cpp"
    if not all(p.is_file() for p in (radio, fifo, meter, component)):
        return False
    return ("SHWM v4.1 FIFO16 experiment" in radio.read_text(encoding="utf-8")
            and "CC1101_FIFOTHR, 0x03" in radio.read_text(encoding="utf-8")
            and "RF_DIAG bytes=" in radio.read_text(encoding="utf-8")
            and "RXBYTES transient count recovered" in radio.read_text(encoding="utf-8")
            and "inline bool retry_invalid_fifo_count" in fifo.read_text(encoding="utf-8")
            and "Key: [REDACTED]" in meter.read_text(encoding="utf-8")
            and "RX_DIAG cumulative" in component.read_text(encoding="utf-8")
            and "SHWM v4.4 stale IRQ clear" in component.read_text(encoding="utf-8")
            and "BaseType_t xHigherPriorityTaskWoken = pdFALSE;" in component.read_text(encoding="utf-8"))


def _restore_tracked_shims(repo_root: Path, components_root: Path) -> None:
    """Migrate in-place from the previous loader which overwrote tracked shims.

    The replacement is always taken from this exact GitHub checkout's HEAD,
    never from the downloaded upstream repository.
    """
    for name in _COMPONENTS:
        stub = components_root / name / "__init__.py"
        if stub.is_file() and _SHIM_SENTINEL in stub.read_text(encoding="utf-8"):
            continue
        path = f"components/{name}/__init__.py"
        tracked_shim = _run(["git", "show", f"HEAD:{path}"], cwd=repo_root)
        if _SHIM_SENTINEL not in tracked_shim:
            raise RuntimeError(f"GitHub component shim not found at {path}")
        stub.parent.mkdir(parents=True, exist_ok=True)
        stub.write_text(tracked_shim + "\n", encoding="utf-8")


def ensure_v4_components(repo_root: Path) -> Path:
    repo_root = repo_root.resolve()
    components_root = repo_root / "components"
    cache_root = components_root / ".shwm_v4_cache"
    lock = FileLock(str(repo_root / ".shwm_v4_install.lock"), timeout=240)

    with lock:
        fingerprint = _fingerprint(repo_root)
        _restore_tracked_shims(repo_root, components_root)
        if _ready(components_root, cache_root, fingerprint):
            return cache_root

        _LOGGER.info("Preparing CC1101 v4 sources from pinned upstream revision.")
        # The marker is written last. An interrupted update cannot be mistaken
        # for a valid prepared cache on the next validation.
        (cache_root / "manifest.sha256").unlink(missing_ok=True)
        with tempfile.TemporaryDirectory(prefix="shwm-wmbus-v4-") as temporary:
            checkout = Path(temporary) / "upstream"
            _run(["git", "clone", "--quiet", _UPSTREAM, str(checkout)])
            _run(["git", "checkout", "--quiet", "--detach", _COMMIT], cwd=checkout)
            if _run(["git", "rev-parse", "HEAD"], cwd=checkout) != _COMMIT:
                raise RuntimeError("wMBus v4 upstream commit SHA did not match")

            for name in _PATCHES:
                patch = str(repo_root / "patches" / name)
                _run(["git", "apply", "--check", patch], cwd=checkout)
                _run(["git", "apply", patch], cwd=checkout)
            _run(["git", "diff", "--check"], cwd=checkout)

            radio = (checkout / "components/wmbus_radio/transceiver_cc1101.cpp")
            meter = (checkout / "components/wmbus_meter/wmbus_meter.cpp")
            radio_text = radio.read_text(encoding="utf-8")
            meter_text = meter.read_text(encoding="utf-8")
            if ('this->write_register(CC1101_MDMCFG4, 0x5C);' not in radio_text or
                    'this->write_register(CC1101_MDMCFG4, 0x6C);' in radio_text or
                    "RF_DIAG bytes=" not in radio_text or
                    "RXBYTES transient count recovered" not in radio_text or
                    "inline bool retry_invalid_fifo_count" not in
                    (checkout / "components/wmbus_radio/cc1101_fifo.h").read_text(encoding="utf-8") or
                    "CC1101_FIFOTHR, 0x03" not in radio_text or
                    "CC1101_FIFOTHR, 0x07" in radio_text or
                    "SHWM v4.1 FIFO16 experiment" not in radio_text or
                    "RX_DIAG cumulative" not in
                    (checkout / "components/wmbus_radio/component.cpp").read_text(encoding="utf-8") or
                    "SHWM v4.4 stale IRQ clear" not in
                    (checkout / "components/wmbus_radio/component.cpp").read_text(encoding="utf-8") or
                    "BaseType_t xHigherPriorityTaskWoken = pdFALSE;" not in
                    (checkout / "components/wmbus_radio/component.cpp").read_text(encoding="utf-8") or
                    "Key: [REDACTED]" not in meter_text or
                    "Key: %s" in meter_text):
                raise RuntimeError("wMBus v4 verification failed")

            for name in _COMPONENTS:
                source = checkout / "components" / name
                if not (source / "__init__.py").is_file():
                    raise RuntimeError(f"Upstream component {name} is missing")
                dest = components_root / name
                dest_cache = cache_root / name
                dest_cache.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source / "__init__.py", dest_cache / "__init__.py")
                # Copy code and licensing notices, but NEVER replace the
                # Git-tracked ESPHome entrypoint in the checkout.
                shutil.copytree(
                    source, dest, dirs_exist_ok=True,
                    ignore=lambda current, names, source=source:
                        {"__init__.py"} if Path(current) == source else set(),
                )

        if not _ready_except_manifest(components_root, cache_root):
            raise RuntimeError("wMBus v4 components did not pass post-install checks")
        (cache_root / "manifest.sha256").write_text(fingerprint + "\n", encoding="ascii")
        _LOGGER.info("CC1101 v4.8 bounded invalid RXBYTES recheck experiment ready; v4.4 stale IRQ clear and FIFO16 preserved; AES keys redacted.")
        return cache_root


def _ready_except_manifest(components_root: Path, cache_root: Path) -> bool:
    """Validate the payload before committing its cache manifest."""
    for name in _COMPONENTS:
        stub = components_root / name / "__init__.py"
        initializer = cache_root / name / "__init__.py"
        if not stub.is_file() or not initializer.is_file():
            return False
        if _SHIM_SENTINEL not in stub.read_text(encoding="utf-8"):
            return False
        if _SHIM_SENTINEL in initializer.read_text(encoding="utf-8"):
            return False
    radio = components_root / "wmbus_radio" / "transceiver_cc1101.cpp"
    fifo = components_root / "wmbus_radio" / "cc1101_fifo.h"
    component = components_root / "wmbus_radio" / "component.cpp"
    meter = components_root / "wmbus_meter" / "wmbus_meter.cpp"
    return (all(p.is_file() for p in (radio, fifo, component, meter))
            and "RF_DIAG bytes=" in radio.read_text(encoding="utf-8")
            and "RXBYTES transient count recovered" in radio.read_text(encoding="utf-8")
            and "inline bool retry_invalid_fifo_count" in fifo.read_text(encoding="utf-8")
            and "RX_DIAG cumulative" in component.read_text(encoding="utf-8")
            and "SHWM v4.4 stale IRQ clear" in component.read_text(encoding="utf-8")
            and "BaseType_t xHigherPriorityTaskWoken = pdFALSE;" in component.read_text(encoding="utf-8")
            and "Key: [REDACTED]" in meter.read_text(encoding="utf-8")
            and "CC1101_FIFOTHR, 0x03" in radio.read_text(encoding="utf-8"))
