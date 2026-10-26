"""ESPHome-compatible loader for pinned CC1101 v4 source components.

The upstream source is fetched and patched on the ESPHome build host
when this external component is imported. The repository itself contains
no third-party source copies.
"""
from pathlib import Path as _shwm_Path

_shwm_repo_root = _shwm_Path(__file__).resolve().parents[2]
_shwm_bootstrap_path = _shwm_repo_root / "components" / "_bootstrap_v4.py"
_shwm_loader = {"__name__": "_shwm_wmbus_v4_bootstrap"}
exec(compile(_shwm_bootstrap_path.read_text(encoding="utf-8"),
             str(_shwm_bootstrap_path), "exec"), _shwm_loader)
_shwm_loader["ensure_v4_components"](_shwm_repo_root)

_shwm_upstream = _shwm_Path(__file__).read_text(encoding="utf-8")
if "_shwm_repo_root" in _shwm_upstream:
    raise RuntimeError("wMBus v4 bootstrap did not install the pinned component")
exec(compile(_shwm_upstream, __file__, "exec"), globals())
