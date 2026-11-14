#!/usr/bin/env bash
set -euo pipefail
for tool in cargo rustc rustup; do
  if command -v "$tool" >/dev/null 2>&1; then
    echo "The consumer image unexpectedly contains $tool" >&2
    exit 1
  fi
done
apt-get update
apt-get install -y --no-install-recommends clang zlib1g-dev python3
python3 eng/build.py consume --version "$PACKAGE_VERSION"
python3 - <<'PY'
import json
from pathlib import Path
result = json.loads(Path('artifacts/consumer-result.json').read_text())
result['rustAbsentFromImagePathBeforeBuild'] = True
result['image'] = 'mcr.microsoft.com/dotnet/sdk:11.0.100-resolute-amd64@sha256:7913685c883a29dd8ba79da96172f5c6b29ed9be706ebe95935e3ef45f19c9c1'
Path('artifacts/pristine-consumer.json').write_text(json.dumps(result, indent=2) + '\n')
PY
