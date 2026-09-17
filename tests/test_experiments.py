"""Re-verify every experiment. This is the reproducibility gate.

    ./start.sh --reset && uv run pytest -q

Each experiment is executed as a subprocess exactly as a reader would run it,
and must exit 0. An experiment exits non-zero when any check comes out
``UNEXPECTED`` -- that is, when a pre-registered expectation does not hold --
so this suite fails loudly if the server's behaviour ever diverges from what
RESULTS.md claims.

Every experiment also cleans up after itself, so the suite is re-runnable and
the experiments can run in any order.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = sorted(p.name for p in (ROOT / "experiments").iterdir() if (p / "run.py").exists())


@pytest.fixture(scope="session", autouse=True)
def lab_is_running() -> None:
    """Fail with a useful message rather than a wall of connection errors."""
    import requests

    if not (ROOT / ".env").exists():
        pytest.fail("No .env found. Start the lab first:  ./start.sh --reset")
    for port in (3000, 3001, 3002):
        try:
            requests.get(f"http://localhost:{port}/", timeout=5)
        except requests.exceptions.RequestException:
            pytest.fail(
                f"Nothing is listening on port {port}. Start the lab:  ./start.sh"
            )


@pytest.mark.parametrize("experiment", EXPERIMENTS)
def test_experiment_runs_and_every_expectation_holds(experiment: str) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "experiments" / experiment / "run.py")],
        capture_output=True, text=True, timeout=900,
    )
    assert result.returncode == 0, (
        f"{experiment} reported an UNEXPECTED result or failed.\n"
        f"--- stdout ---\n{result.stdout[-4000:]}\n--- stderr ---\n{result.stderr[-2000:]}"
    )


@pytest.mark.parametrize("experiment", EXPERIMENTS)
def test_result_file_is_complete(experiment: str) -> None:
    """Every experiment must leave a result behind that RESULTS.md can cite."""
    payload = json.loads((ROOT / "experiments" / experiment / "result.json").read_text())
    assert payload["checks"], f"{experiment} recorded no checks"
    assert payload["unexpected"] == 0
    assert payload["summary"].strip()
    for check in payload["checks"]:
        assert check["status"] in {"ENFORCED", "DECLARED-ONLY", "NOT-SUPPORTED"}


@pytest.mark.parametrize("experiment", EXPERIMENTS)
def test_evidence_contains_no_credentials(experiment: str) -> None:
    """Evidence transcripts are committed, so they must never carry secrets."""
    evidence = ROOT / "experiments" / experiment / "evidence"
    text = "\n".join(p.read_text() for p in evidence.glob("transcript.*"))
    assert "<redacted>" in text, "expected redaction markers in the transcript"

    env = (ROOT / ".env").read_text().splitlines()
    secrets = [
        line.split("=", 1)[1]
        for line in env
        if line.startswith(("ALICE_CLIENT_SECRET", "BOB_CLIENT_SECRET", "ALICE2_CLIENT_SECRET"))
    ]
    for secret in secrets:
        if secret:
            assert secret not in text, "a client secret leaked into the evidence transcript"
