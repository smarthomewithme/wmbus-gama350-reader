#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UPSTREAM="$ROOT/vendor/upstream"
PATCH="$ROOT/patches/0003-cc1101-stable-rxbytes.patch"

if [[ ! -d "$UPSTREAM/.git" ]]; then
  echo "Missing vendor/upstream. Run scripts/prepare_sources.sh first." >&2
  exit 2
fi

if git -C "$UPSTREAM" apply --reverse --check "$PATCH" 2>/dev/null; then
  echo "CC1101 stable RXBYTES patch is already enabled."
  exit 0
fi

git -C "$UPSTREAM" apply --check "$PATCH"
git -C "$UPSTREAM" apply "$PATCH"
git -C "$UPSTREAM" diff --check
echo "CC1101 stable RXBYTES patch enabled. No firmware has been flashed."
git -C "$UPSTREAM" diff --stat
