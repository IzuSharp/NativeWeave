#!/usr/bin/env bash
# Database candidate closure in the Linux row; no public publication.
set -euo pipefail
cd "$(dirname "$0")/.."
db_scope_output=artifacts/db-scope
test -f "$db_scope_output/prepared/manifest.json"
python3 tests/Packaging.Domain/test_release_results.py

db_scope_sdk='mcr.microsoft.com/dotnet/sdk:11.0.100-resolute-amd64@sha256:7913685c883a29dd8ba79da96172f5c6b29ed9be706ebe95935e3ef45f19c9c1'
docker run --rm --network host \
  -v "$PWD:/work:ro" -v "$PWD/artifacts:/work/artifacts" -w /work \
  -e NW_TEST_POSTGRES -e DOTNET_CLI_TELEMETRY_OPTOUT=1 \
  -e B24_PRISTINE_IMAGE="$db_scope_sdk" "$db_scope_sdk" bash -c '
    set -euo pipefail
    for tool in cargo rustc rustup; do
      if command -v "$tool" >/dev/null 2>&1; then
        echo "The pristine database consumer image unexpectedly contains $tool" >&2
        exit 1
      fi
    done
    apt-get update
    apt-get install -y --no-install-recommends clang zlib1g-dev python3
    git config --global --add safe.directory /work
    python3 tests/Packaging.Domain/release_cases.py \
      --manifest /work/artifacts/db-scope/prepared/manifest.json \
      --output /work/artifacts/db-scope/release --consumer-environment pristine
  '

# Only the verified AOT output and standalone verifier enter this runtime image.
db_scope_runtime='mcr.microsoft.com/dotnet/runtime-deps:10.0.15-noble-amd64@sha256:ebb73a172b49758c6de2462305e872ea0cb37ad3ca27cc0d86bc48b6271eaace'
mkdir -p "$db_scope_output/runtime"
docker run --rm --network host \
  -v "$PWD/$db_scope_output/release/candidate-destination/runtime-transfer:/input:ro" \
  -v "$PWD/tests/Packaging.Domain/runtime_verify.py:/verify.py:ro" \
  -v "$PWD/$db_scope_output/runtime:/result" \
  -e NW_TEST_POSTGRES -e B24_RUNTIME_IMAGE="$db_scope_runtime" "$db_scope_runtime" bash -c '
    set -euo pipefail
    apt-get update
    apt-get install -y --no-install-recommends python3
    python3 /verify.py --bundle /input --output /result/evidence
  '
mkdir -p "$db_scope_output/evidence"
docker image inspect "$db_scope_sdk" "$db_scope_runtime" > "$db_scope_output/evidence/images.json"
