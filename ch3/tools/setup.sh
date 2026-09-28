#!/usr/bin/env bash
# npm run exp:setup [-- --reset]
# Installs pinned deps, starts CSS 7.2.0 WAC on :3100 and ACP on :3101 (seeded),
# mints client credentials, then writes ch3/results/ENVIRONMENT.md.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
if [[ -f "$ROOT/.nvmrc" && "$(node -v)" != "v$(cat "$ROOT/.nvmrc")" ]]; then
  echo "WARNING: node $(node -v) differs from .nvmrc (v$(cat "$ROOT/.nvmrc")); recorded in ENVIRONMENT.md" >&2
fi
bash ch3/start.sh "$@"
if [[ -f ch3/phases/p4_comunica/package-lock.json && ! -d ch3/phases/p4_comunica/node_modules ]]; then
  (cd ch3/phases/p4_comunica && npm ci --no-audit --no-fund >/dev/null)
fi
uv run python -m ch3.tools.environment
