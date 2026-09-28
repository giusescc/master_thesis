"""Where Chapter 3 lives: ports, paths, and the git-ignored credentials file."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values

CH3 = Path(__file__).resolve().parents[1]
ROOT = CH3.parent
STATE = CH3 / ".state"
ENV_PATH = STATE / ".env"
LOGS = STATE / "logs"
RESULTS = CH3 / "results"
RAW = RESULTS / "raw"

#: The two server configurations every phase runs on.
CONFIGS = {
    "wac": {"port": 3100, "config": "ch3/config/css-wac.json", "authz": "WAC"},
    "acp": {"port": 3101, "config": "ch3/config/css-acp.json", "authz": "ACP"},
}

AGENTS = ("alice", "appr", "bob")

#: The one fixed random seed. Logged in every run header.
SEED = 20260924


def base_url(config: str) -> str:
    return f"http://localhost:{CONFIGS[config]['port']}/"


@dataclass
class Identity:
    name: str
    config: str
    issuer: str
    pod_url: str
    web_id: str
    client_id: str
    client_secret: str


def identity(config: str, agent: str) -> Identity:
    if not ENV_PATH.exists():
        raise SystemExit("No ch3/.state/.env. Start the servers first: npm run exp:setup")
    values = dotenv_values(ENV_PATH)
    prefix = f"{config.upper()}_{agent.upper()}_"

    def need(key: str) -> str:
        value = values.get(prefix + key)
        if not value:
            raise SystemExit(f"{prefix}{key} missing from ch3/.state/.env; run npm run exp:setup -- --reset")
        return value

    return Identity(
        name=agent,
        config=config,
        issuer=base_url(config),
        pod_url=need("POD"),
        web_id=need("WEBID"),
        client_id=need("CLIENT_ID"),
        client_secret=need("CLIENT_SECRET"),
    )


def full_run() -> int:
    """Which full run (1 or 2) the current invocation belongs to."""
    return int(os.environ.get("CH3_FULL_RUN", "1"))
