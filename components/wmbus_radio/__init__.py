"""Load the exact pinned upstream ESPHome component without modifying this stub.

The component's upstream initializer is cached separately so GitHub source
refreshes cannot restore this shim while a stale ready-marker is present.
"""
from pathlib import Path as _shwm_Path

_shwm_repo_root = _shwm_Path(__file__).resolve().parents[2]
_shwm_bootstrap_path = _shwm_repo_root / "components" / "_bootstrap_v4.py"
_shwm_loader = {"__name__": "_shwm_wmbus_v4_bootstrap"}
exec(compile(_shwm_bootstrap_path.read_text(encoding="utf-8"),
             str(_shwm_bootstrap_path), "exec"), _shwm_loader)
_shwm_cache = _shwm_loader["ensure_v4_components"](_shwm_repo_root)
_shwm_initializer = _shwm_cache / _shwm_Path(__file__).parent.name / "__init__.py"
if not _shwm_initializer.is_file():
    raise RuntimeError("wMBus v4 upstream initializer is missing from the verified cache")
_shwm_source = _shwm_initializer.read_text(encoding="utf-8")
if "_shwm_wmbus_v4_bootstrap" in _shwm_source:
    raise RuntimeError("wMBus v4 cache contains a bootstrap shim instead of upstream code")
exec(compile(_shwm_source, str(_shwm_initializer), "exec"), globals())
