#!/usr/bin/env bash
#
# Start (or restart) the whole lab with one command.
#
#   ./start.sh            resume: bring the servers back up, keep existing data
#   ./start.sh --reset    clean room: wipe all pod data and re-provision users
#   ./start.sh --stop     stop everything and exit
#
# Three processes are managed:
#   :3000  Community Solid Server, pod provider A  (./data)
#   :3001  Community Solid Server, pod provider B  (./data2)
#   :3002  static host for a provider-independent WebID (./webid)
#
# Every version is pinned (CSS 7.2.0 via package-lock.json, Python 3.12 via
# uv.lock) so a clean checkout reproduces the published results.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

LOGS="$ROOT/logs"
mkdir -p "$LOGS"

RESET=0
STOP_ONLY=0
for arg in "$@"; do
  case "$arg" in
    --reset) RESET=1 ;;
    --stop)  STOP_ONLY=1 ;;
    -h|--help) sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown option: $arg (try --help)" >&2; exit 2 ;;
  esac
done

say() { printf '\033[1m%s\033[0m\n' "$*"; }

# Stop only the processes THIS script started, tracked by pidfile. We never
# pattern-match across the whole process table: that risks killing something
# outside this project.
stop_one() {
  local name="$1"
  local pidfile="$LOGS/$name.pid"
  if [[ -f "$pidfile" ]]; then
    local pid; pid="$(cat "$pidfile")"
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      for _ in $(seq 1 40); do kill -0 "$pid" 2>/dev/null || break; sleep 0.25; done
      kill -9 "$pid" 2>/dev/null || true
    fi
    rm -f "$pidfile"
  fi
}

stop_all() {
  say "Stopping lab processes..."
  stop_one css-3000
  stop_one css-3001
  stop_one webid-3002
}

wait_for_http() {
  local url="$1"
  local name="$2"
  local tries="${3:-90}"
  for _ in $(seq 1 "$tries"); do
    if curl -sf -o /dev/null "$url" 2>/dev/null; then return 0; fi
    sleep 1
  done
  echo "ERROR: $name did not become ready at $url" >&2
  echo "--- last 30 log lines ---" >&2
  tail -30 "$LOGS/$name.log" >&2 || true
  return 1
}

start_css() {
  local port="$1"
  local dir="$2"
  local name="css-$port"
  say "Starting CSS on :$port (storage: $dir)"
  mkdir -p "$dir"
  npx --no-install community-solid-server \
      -p "$port" -c @css:config/file.json -f "$dir" -l warn \
      > "$LOGS/$name.log" 2>&1 &
  echo $! > "$LOGS/$name.pid"
  wait_for_http "http://localhost:$port/" "$name"
}

stop_all
if [[ "$STOP_ONLY" -eq 1 ]]; then say "Stopped."; exit 0; fi

if [[ "$RESET" -eq 1 ]]; then
  say "--reset: wiping pod storage, WebID host and credentials"
  rm -rf "$ROOT/data" "$ROOT/data2" "$ROOT/webid" "$ROOT/.env"
fi

# Dependencies must be present and pinned before anything starts.
if [[ ! -d "$ROOT/node_modules/@solid/community-server" ]]; then
  say "Installing pinned Node dependencies (CSS 7.2.0)"
  npm ci --no-audit --no-fund > "$LOGS/npm-install.log" 2>&1 \
    || npm install --no-audit --no-fund > "$LOGS/npm-install.log" 2>&1
fi
say "Syncing pinned Python environment (3.12)"
uv sync --extra dev --quiet

start_css 3000 "$ROOT/data"
start_css 3001 "$ROOT/data2"

say "Starting WebID host on :3002"
mkdir -p "$ROOT/webid"
printf '# placeholder, replaced by experiments/03_portability\n' > "$ROOT/webid/index.txt"
uv run python "$ROOT/scripts/webid_host.py" 3002 > "$LOGS/webid-3002.log" 2>&1 &
echo $! > "$LOGS/webid-3002.pid"
wait_for_http "http://localhost:3002/index.txt" "webid-3002"

if [[ ! -f "$ROOT/.env" ]]; then
  say "Provisioning users (alice, bob on A; alice2 on B)"
  uv run python "$ROOT/scripts/seed.py"
else
  say "Reusing existing .env (use --reset to re-provision)"
fi

cat <<EOF

$(say "Lab is up.")
  Pod provider A   http://localhost:3000/   (alice, bob)
  Pod provider B   http://localhost:3001/   (alice2)
  WebID host       http://localhost:3002/   (independent identity, experiment 03)
  Logs             logs/*.log
  Credentials      .env  (git-ignored, never printed)

Run the experiments:
  uv run python experiments/00_hello_pod/run.py
  uv run pytest -q        # re-verifies every experiment

Stop the lab:
  ./start.sh --stop
EOF
