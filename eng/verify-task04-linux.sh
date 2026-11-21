#!/usr/bin/env bash
# Retained Core ABI/lifecycle package, minimum CPU and runtime transfer gates.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 tests/Packaging.Linux/verify.py --require-baseline --output artifacts/task04/A14/ci
python3 tests/Packaging.Linux/minimum_cpu.py artifacts/task04/A14/ci/runtime-transfer \
  --output artifacts/task04/A14/minimum-cpu --require-baseline

# A16's unique package-task/release guards now run against the actual database
# packages in Packaging.Domain; no artificial product or generator package remains.
runtime_image='mcr.microsoft.com/dotnet/runtime-deps:10.0.15-noble-amd64@sha256:ebb73a172b49758c6de2462305e872ea0cb37ad3ca27cc0d86bc48b6271eaace'
mkdir -p artifacts/task04/runtime
docker run --rm \
  -v "$PWD/artifacts/task04/A14/ci/runtime-transfer:/input/a14:ro" \
  -v "$PWD/tests/Packaging.Linux/runtime.py:/verify-a14.py:ro" \
  -v "$PWD/artifacts/task04/runtime:/result" "$runtime_image" bash -c '
    set -euo pipefail
    apt-get update
    apt-get install -y --no-install-recommends python3
    python3 /verify-a14.py /input/a14 --receipt /result/a14.json --require-tool-absence
  '
docker image inspect "$runtime_image" > artifacts/task04/runtime/images.json
