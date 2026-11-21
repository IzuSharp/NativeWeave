#!/usr/bin/env bash
# Maintainer-only PostgreSQL 18 binaries for the retained TLS/process fault tests.
set -euo pipefail
cd "$(dirname "$0")/.."
db_scope_pg_root="$PWD/artifacts/postgres-tools"
test ! -e "$db_scope_pg_root"
mkdir -p "$db_scope_pg_root"
curl --fail --location --retry 3 \
  https://ftp.postgresql.org/pub/source/v18.0/postgresql-18.0.tar.bz2 \
  -o "$db_scope_pg_root/postgresql-18.0.tar.bz2"
python3 - "$db_scope_pg_root/postgresql-18.0.tar.bz2" <<'PY'
import hashlib,sys
from pathlib import Path
assert hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest() == "0d5b903b1e5fe361bca7aa9507519933773eb34266b1357c4e7780fdee6d6078"
PY
tar -xf "$db_scope_pg_root/postgresql-18.0.tar.bz2" -C "$db_scope_pg_root"
cd "$db_scope_pg_root/postgresql-18.0"
./configure --prefix="$db_scope_pg_root/install" --without-icu --without-readline --with-ssl=openssl > "$db_scope_pg_root/configure.log"
make -j2 > "$db_scope_pg_root/build.log"
make install > "$db_scope_pg_root/install.log"
"$db_scope_pg_root/install/bin/postgres" --version
if [ -n "${GITHUB_ENV:-}" ]; then
  echo "NW_POSTGRES_BIN=$db_scope_pg_root/install/bin" >> "$GITHUB_ENV"
  echo "$db_scope_pg_root/install/bin" >> "$GITHUB_PATH"
fi
