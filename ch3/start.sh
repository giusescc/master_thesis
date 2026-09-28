#!/usr/bin/env bash
#
# Start (or restart) the Chapter 3 servers. Chapter 2's lab (:3000-3002) is
# never touched: Chapter 3 has its own ports, data dirs, pidfiles and logs.
#
#   ch3/start.sh                     resume: bring both servers up, keep data
#   ch3/start.sh --reset             clean room: wipe Ch3 pod data + credentials
#   ch3/start.sh --stop              stop both servers and exit
#   ch3/start.sh --expiry short wac  restart ONE server with its short-expiry
#   ch3/start.sh --expiry default wac   config (maxDuration 2 min) or back to
#                                    the default config, on the same data dir
#
#   :3100  CSS 7.2.0, config ch3/config/css-wac.json  (ch3/.state/data-wac)
#   :3101  CSS 7.2.0, config ch3/config/css-acp.json  (ch3/.state/data-acp)
#
# Accounts and pods (alice, appr, bob) come from CSS --seedConfig
# (ch3/config/seed.json) on the first start of an empty data dir. Client
# credentials cannot be seeded, so ch3/tools/provision.py mints them afterwards
# into ch3/.state/.env (git-ignored, never printed).

set -euo pipefail

CH3="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$CH3/.." && pwd)"
STATE="$CH3/.state"
LOGS="$STATE/logs"
mkdir -p "$LOGS"
cd "$ROOT"

RESET=0
STOP_ONLY=0
EXPIRY=""
EXPIRY_CFG=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --reset) RESET=1 ;;
    --stop)  STOP_ONLY=1 ;;
    --expiry) EXPIRY="$2"; EXPIRY_CFG="$3"; shift 2 ;;
    -h|--help) sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown option: $1 (try --help)" >&2; exit 2 ;;
  esac
  shift
done

say() { printf '\033[1m%s\033[0m\n' "$*"; }

port_of() { case "$1" in wac) echo 3100 ;; acp) echo 3101 ;; esac; }

# Stop only processes this script started, tracked by pidfile.
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

wait_for_http() {
  local url="$1" name="$2"
  for _ in $(seq 1 90); do
    if curl -sf -o /dev/null "$url" 2>/dev/null; then return 0; fi
    sleep 1
  done
  echo "ERROR: $name did not become ready at $url" >&2
  tail -30 "$LOGS/$name.log" >&2 || true
  return 1
}

# start_css <wac|acp> <default|short>
start_css() {
  local cfg="$1" expiry="$2"
  local port; port="$(port_of "$cfg")"
  local name="css-$cfg"
  local dir="$STATE/data-$cfg"
  local config="$CH3/config/css-$cfg.json"
  [[ "$expiry" == "short" ]] && config="$CH3/config/css-$cfg-short.json"
  local seed=()
  if [[ ! -d "$dir" ]]; then seed=(--seedConfig "$CH3/config/seed.json"); fi
  mkdir -p "$dir"
  say "Starting CSS on :$port ($cfg, expiry=$expiry)"
  # Each start gets its own log file; the latest is linked as $name.log.
  local log="$LOGS/$name-$(date -u +%Y%m%dT%H%M%SZ).log"
  npx --no-install community-solid-server \
      -p "$port" -c "$config" -f "$dir" -l info ${seed[@]+"${seed[@]}"} \
      > "$log" 2>&1 &
  echo $! > "$LOGS/$name.pid"
  echo "$expiry" > "$LOGS/$name.expiry"
  ln -sf "$(basename "$log")" "$LOGS/$name.log"
  wait_for_http "http://localhost:$port/" "$name"
}

if [[ -n "$EXPIRY" ]]; then
  [[ "$EXPIRY" == "short" || "$EXPIRY" == "default" ]] || { echo "--expiry short|default <wac|acp>" >&2; exit 2; }
  [[ "$EXPIRY_CFG" == "wac" || "$EXPIRY_CFG" == "acp" ]] || { echo "--expiry short|default <wac|acp>" >&2; exit 2; }
  stop_one "css-$EXPIRY_CFG"
  start_css "$EXPIRY_CFG" "$EXPIRY"
  exit 0
fi

say "Stopping Chapter 3 servers..."
stop_one css-wac
stop_one css-acp
if [[ "$STOP_ONLY" -eq 1 ]]; then say "Stopped."; exit 0; fi

if [[ "$RESET" -eq 1 ]]; then
  say "--reset: wiping Chapter 3 pod data and credentials"
  rm -rf "$STATE/data-wac" "$STATE/data-acp" "$STATE/.env"
fi

if [[ ! -d "$ROOT/node_modules/@solid/community-server" ]]; then
  say "Installing pinned Node dependencies (CSS 7.2.0)"
  npm ci --no-audit --no-fund > "$LOGS/npm-install.log" 2>&1
fi
say "Syncing pinned Python environment (3.12)"
uv sync --extra dev --quiet

start_css wac default
start_css acp default

if [[ ! -f "$STATE/.env" ]]; then
  say "Minting client credentials (alice, appr, bob on both servers)"
  uv run python -m ch3.tools.provision
else
  say "Reusing existing ch3/.state/.env (use --reset to re-provision)"
fi

say "Chapter 3 servers are up: WAC http://localhost:3100/  ACP http://localhost:3101/"
