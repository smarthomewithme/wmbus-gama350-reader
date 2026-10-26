#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "\${BASH_SOURCE[0]}")/.." && pwd)"
UPSTREAM="https://github.com/SzczepanLeon/esphome-components.git"
SHA="a732dd0e52c48973fad57e4950a11d8e2f2d6820"
DEST="$ROOT/vendor/upstream"
PATCH="$ROOT/patches/0001-safe-packet-decoder-and-cc1101-fifo.patch"
if [[ -e "$DEST" ]]; then
  echo "Refusing to modify existing directory $DEST. Back it up/remove it explicitly." >&2
  exit 2
fi
mkdir -p "$ROOT/vendor"
git clone "$UPSTREAM" "$DEST"
git -C "$DEST" checkout --detach "$SHA"
ACTUAL="$(git -C "$DEST" rev-parse HEAD)"
if [[ "$ACTUAL" != "$SHA" ]]; then echo "SHA mismatch: $ACTUAL" >&2; exit 3; fi
git -C "$DEST" apply --check "$PATCH"
git -C "$DEST" apply "$PATCH"
echo "Pinned upstream: $ACTUAL"
git -C "$DEST" diff --stat
