"""Regression: an ESPHome Git refresh must not invalidate prepared v4 sources.

Run with: python tests/test_bootstrap_refresh.py
This is a local synthetic-cache test; no meter, secret, or network is used.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import sys
import tempfile
import types
from contextlib import nullcontext
from unittest.mock import patch

REPOSITORY = Path(__file__).resolve().parents[1]
NAMES = ("wmbus_common", "wmbus_radio", "wmbus_meter", "socket_transmitter")
BOOTSTRAP = REPOSITORY / "components" / "_bootstrap_v4.py"

spec = importlib.util.spec_from_file_location("shwm_v4_bootstrap_test", BOOTSTRAP)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
# Native test jobs run before ESPHome (and its 'filelock' dependency) is
# installed. Provide a test-only no-op lock for this single-threaded fixture.
try:
    import filelock  # noqa: F401
    spec.loader.exec_module(module)
except ModuleNotFoundError as exc:
    if exc.name != "filelock":
        raise
    shim = types.SimpleNamespace(FileLock=lambda *args, **kwargs: nullcontext())
    with patch.dict(sys.modules, {"filelock": shim}):
        spec.loader.exec_module(module)

with tempfile.TemporaryDirectory(prefix="wmbus-v4-refresh-test-") as temp:
    root = Path(temp)
    (root / "patches").mkdir(parents=True)
    for patch_name in module._PATCHES:
        shutil.copy2(REPOSITORY / "patches" / patch_name,
                     root / "patches" / patch_name)

    component_root = root / "components"
    cache = component_root / ".shwm_v4_cache"
    expected_shims = {}

    for name in NAMES:
        shim = (REPOSITORY / "components" / name / "__init__.py").read_text(
            encoding="utf-8")
        expected_shims[name] = shim
        (component_root / name).mkdir(parents=True)
        (component_root / name / "__init__.py").write_text(
            shim, encoding="utf-8")
        (cache / name).mkdir(parents=True)
        (cache / name / "__init__.py").write_text(
            "# pinned upstream component initializer; not a bootstrap shim\n",
            encoding="utf-8")

    (component_root / "wmbus_radio" / "transceiver_cc1101.cpp").write_text(
        "// RF_DIAG bytes=; CC1101_MDMCFG4 0x5C; CC1101_FIFOTHR, 0x03; SHWM v4.1 FIFO16 experiment; SHWM v4.9 MARCSTATE EOF confirmation; confirm_marcstate_eof(\n", encoding="utf-8")
    (component_root / "wmbus_radio" / "cc1101_fifo.h").write_text(
        "// inline bool confirm_marcstate_eof( test fixture\\n", encoding="utf-8")
    (component_root / "wmbus_radio" / "component.cpp").write_text(
        "// RX_DIAG cumulative; SHWM v4.4 stale IRQ clear; BaseType_t xHigherPriorityTaskWoken = pdFALSE;\n", encoding="utf-8")
    (component_root / "wmbus_meter" / "wmbus_meter.cpp").write_text(
        "// Key: [REDACTED]\n", encoding="utf-8")

    signature = module._fingerprint(root)
    (cache / "manifest.sha256").write_text(signature + "\n", encoding="ascii")

    # Initial use and subsequent import MUST leave every tracked entrypoint
    # untouched. No network checkout should occur with a valid cache.
    with patch.object(module, "_run", side_effect=AssertionError(
            "Unexpected Git operation with a fully prepared cache")):
        assert module.ensure_v4_components(root) == cache
        assert module.ensure_v4_components(root) == cache

    for name, expected in expected_shims.items():
        assert (component_root / name / "__init__.py").read_text(
            encoding="utf-8") == expected

    # Reproduce real v4 error: the OLD loader had overwritten a tracked shim
    # with the upstream initializer, then GitHub refreshed the checkout.
    # The new loader must restore the checked-out shim without cloning
    # upstream or treating the stale marker as sufficient.
    broken = component_root / "socket_transmitter" / "__init__.py"
    broken.write_text("# old upstream initializer overwrote tracked shim\n",
                      encoding="utf-8")
    calls = []

    def simulate_git_show(args, *, cwd=None):
        calls.append(tuple(args))
        assert args == ["git", "show",
                        "HEAD:components/socket_transmitter/__init__.py"]
        assert cwd == root
        return expected_shims["socket_transmitter"].rstrip("\n")

    with patch.object(module, "_run", side_effect=simulate_git_show):
        assert module.ensure_v4_components(root) == cache

    assert len(calls) == 1
    assert broken.read_text(encoding="utf-8") == (
        expected_shims["socket_transmitter"])
    for name in NAMES:
        assert (cache / name / "__init__.py").read_text(
            encoding="utf-8").startswith("# pinned upstream")

    # Change to a patch MUST invalidate the ready cache fingerprint.
    original_patch = root / "patches" / module._PATCHES[0]
    original_patch.write_bytes(original_patch.read_bytes() + b"\n# test\n")
    assert module._fingerprint(root) != signature
    assert not module._ready(component_root, cache, module._fingerprint(root))

print("BOOTSTRAP_REFRESH_REGRESSION_PASS: idempotent, restored shim, cache invalidation")
