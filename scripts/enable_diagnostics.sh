#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/vendor/upstream"
PATCH="$ROOT/patches/0002-cc1101-long-frame-diagnostics.patch"

if [[ ! -d "$SRC/.git" ]]; then
  echo "Missing vendor/upstream. Run scripts/prepare_sources.sh first." >&2
  exit 2
fi
if git -C "$SRC" apply --reverse --check "$PATCH" 2>/dev/null; then
  echo "Long-frame diagnostics are already enabled."
  exit 0
fi
git -C "$SRC" apply --check "$PATCH"
git -C "$SRC" apply "$PATCH"
git -C "$SRC" diff --check
echo "Long-frame RX diagnostics enabled. No firmware has been flashed."
git -C "$SRC" diff --stat
