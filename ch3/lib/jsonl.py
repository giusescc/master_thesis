"""Raw evidence: one JSONL file per run, created once and never overwritten.

Every line carries:

* ``ts``   ISO 8601 UTC with milliseconds, e.g. ``2026-09-24T14:08:27.772Z``
* ``seq``  line number within the run
* ``t_ms`` monotonic milliseconds since the run started (for latencies; wall
  clocks can step, ``time.perf_counter`` cannot)
* ``event`` what happened

The first line is ``run_start`` (phase, config, variant, rep, seed, full_run,
git commit). The last line of a completed run is ``summary`` with a categorical
``outcome`` dict (compared across full runs by ``exp:compare``) and ``metrics``
(timings, never compared for equality).

Files are opened with ``O_EXCL``, so an existing file can never be replaced.
When a run closes, its sha256 is appended to ``raw/MANIFEST.sha256``; ``exp:check``
and ``exp:compare`` re-hash every file against it, so a file modified after its
run is detected.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ch3.lib.env import RAW, RESULTS, ROOT, SEED, full_run

MANIFEST = RAW / "MANIFEST.sha256"
SCRATCH = RESULTS / "scratch"


def utc_ms() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def git_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:  # noqa: BLE001 -- recorded, not fatal
        return "unknown"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RunLog:
    def __init__(self, phase: str, config: str, variant: str, rep: int, scratch: bool = False) -> None:
        self.phase, self.config, self.variant, self.rep = phase, config, variant, rep
        self.scratch = scratch
        base = SCRATCH if scratch else RAW
        directory = base / phase / config
        directory.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%f")[:-3] + "Z"
        self.run_id = f"{stamp}-{variant}-r{rep:02d}"
        self.path = directory / f"{self.run_id}.jsonl"
        fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        self._fh = os.fdopen(fd, "w", encoding="utf-8")
        self._seq = 0
        self._lock = threading.Lock()
        self._t0 = time.perf_counter()
        self.closed = False
        self.write(
            "run_start",
            phase=phase, config=config, variant=variant, rep=rep,
            condition=f"{phase}/{config}/{variant}", run_id=self.run_id,
            seed=SEED, full_run=full_run(), scratch=scratch, git_commit=git_commit(),
        )

    def t_ms(self) -> float:
        return round((time.perf_counter() - self._t0) * 1000, 3)

    def write(self, event: str, **fields: Any) -> dict:
        with self._lock:  # pollers and receivers write from their own threads
            line = {"ts": utc_ms(), "seq": self._seq, "t_ms": self.t_ms(), "event": event, **fields}
            self._fh.write(json.dumps(line, ensure_ascii=False, default=str) + "\n")
            self._fh.flush()
            self._seq += 1
        return line

    def summary(self, outcome: dict[str, Any], metrics: dict[str, Any] | None = None) -> None:
        self.write("summary", outcome=outcome, metrics=metrics or {})

    def close(self) -> None:
        if self.closed:
            return
        self.write("run_end")
        self._fh.flush()
        os.fsync(self._fh.fileno())
        self._fh.close()
        self.closed = True
        if not self.scratch:
            rel = self.path.relative_to(RAW)
            with open(MANIFEST, "a", encoding="utf-8") as manifest:
                manifest.write(f"{sha256(self.path)}  {rel}\n")


def read_run(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
