#!/usr/bin/env bash
# Standalone ordinary database consumer inside the pinned SDK image.
set -euo pipefail
for tool in cargo rustc rustup; do
  if command -v "$tool" >/dev/null 2>&1; then
    echo "The consumer image unexpectedly contains $tool" >&2
    exit 1
  fi
done
apt-get update
apt-get install -y --no-install-recommends clang zlib1g-dev python3
python3 eng/build.py consume --consumer-environment pristine
