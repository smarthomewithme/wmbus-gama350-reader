#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
CXX="${CXX:-g++}"
for src in tests/regression.cpp tests/fifo_model.cpp; do
  output="$(mktemp /tmp/wmbus-test.XXXXXX)"
  trap 'rm -f "$output"' EXIT
  "$CXX" -std=c++17 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined -fno-omit-frame-pointer "$src" -o "$output"
  ASAN_OPTIONS=detect_leaks=0 "$output"
  rm -f "$output"
done
python3 -m unittest discover -s tests -p 'test_*.py' -v
