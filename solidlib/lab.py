"""Load the lab's configuration and hand experiments ready-made sessions.

Reads ``.env`` (written by ``./start.sh``) so that no experiment ever contains a
credential, a WebID or a port number in its source.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from solidlib.evidence import EvidenceLog
from solidlib.provision import PodIdentity
from solidlib.session import SolidSession

ROOT = Path(__file__).resolve().parents[1]


def load() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        raise SystemExit(
            "No .env found. Start the lab first:\n"
            "    ./start.sh --reset\n"
        )
    load_dotenv(env_path)


def _identity(prefix: str) -> PodIdentity:
    def need(key: str) -> str:
        value = os.environ.get(f"{prefix}_{key}")
        if not value:
            raise SystemExit(
                f"{prefix}_{key} missing from .env -- re-run ./start.sh --reset"
            )
        return value

    return PodIdentity(
        email=need("EMAIL"),
        pod_url=need("POD"),
        web_id=need("WEBID"),
        client_id=need("CLIENT_ID"),
        client_secret=need("CLIENT_SECRET"),
    )


def issuer(prefix: str) -> str:
    return os.environ[f"{prefix}_ISSUER"]


def session(prefix: str, evidence: EvidenceLog | None = None, name: str | None = None) -> SolidSession:
    """Build an authenticated session for one of the lab users."""
    load()
    identity = _identity(prefix)
    return SolidSession.from_identity(
        name=name or prefix.capitalize(),
        base_url=issuer(prefix),
        identity=identity,
        evidence=evidence,
    )


def anonymous(base_prefix: str = "ALICE", evidence: EvidenceLog | None = None) -> SolidSession:
    """An unauthenticated client pointed at the same server as ``base_prefix``."""
    load()
    return SolidSession.anonymous(issuer(base_prefix), evidence=evidence)


def evidence_for(experiment_dir: Path | str, name: str) -> EvidenceLog:
    return EvidenceLog(Path(experiment_dir) / "evidence", name)
