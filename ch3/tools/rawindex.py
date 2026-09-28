"""Read ``ch3/results/raw/`` back: runs by condition and full run, plus integrity."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from ch3.lib.env import RAW
from ch3.lib.jsonl import MANIFEST, sha256

TS = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")


@dataclass
class Run:
    path: Path
    condition: tuple[str, str, str]
    full_run: int
    completed: bool          # has a summary line and no run_error
    bad_ts_lines: list[int]  # line numbers without a valid ts
    outcome: dict | None
    suspended_s: float = 0.0  # wall-clock minus monotonic span; > threshold = spanned a suspend


EXCLUDED = RAW / "EXCLUDED.tsv"


def excluded() -> dict[str, str]:
    """Raw files kept on disk but not counted, with the documented reason.

    Format: ``<path relative to raw/>\\t<reason>``. A run is excluded only when
    the instrument (not the system under test) was at fault; each exclusion is
    also described in OBSERVATIONS.md.
    """
    if not EXCLUDED.exists():
        return {}
    out = {}
    for line in EXCLUDED.read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            rel, reason = line.split("\t", 1)
            out[rel] = reason
    return out


def load_runs() -> list[Run]:
    runs = []
    skip = excluded()
    for path in sorted(RAW.glob("p*/*/*.jsonl")):
        if str(path.relative_to(RAW)) in skip:
            continue
        bad, lines = [], []
        for n, text in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            try:
                line = json.loads(text)
            except json.JSONDecodeError:
                bad.append(n)
                continue
            if not isinstance(line.get("ts"), str) or not TS.match(line["ts"]):
                bad.append(n)
            lines.append(line)
        start = next((l for l in lines if l.get("event") == "run_start"), {})
        summary = next((l for l in lines if l.get("event") == "summary"), None)
        errored = any(l.get("event") == "run_error" for l in lines)
        runs.append(Run(
            path=path,
            condition=(start.get("phase", "?"), start.get("config", "?"), start.get("variant", "?")),
            full_run=int(start.get("full_run", 0)),
            completed=summary is not None and not errored,
            bad_ts_lines=bad,
            outcome=summary.get("outcome") if summary else None,
            suspended_s=suspended_seconds(lines),
        ))
    return runs


SUSPEND_THRESHOLD_S = 5.0


def suspended_seconds(lines: list[dict]) -> float:
    """Wall-clock span minus monotonic span of a run, in seconds.

    ``ts`` is wall clock; ``t_ms`` is a monotonic clock, which on macOS stops
    while the machine sleeps. A difference above SUSPEND_THRESHOLD_S means the
    run spanned a system suspend, so its timed windows are not valid.
    """
    timed = [l for l in lines if isinstance(l.get("t_ms"), (int, float)) and isinstance(l.get("ts"), str)]
    if len(timed) < 2:
        return 0.0
    try:
        wall = (datetime.fromisoformat(timed[-1]["ts"].replace("Z", "+00:00"))
                - datetime.fromisoformat(timed[0]["ts"].replace("Z", "+00:00"))).total_seconds()
    except ValueError:
        return 0.0
    return round(wall - (timed[-1]["t_ms"] - timed[0]["t_ms"]) / 1000, 1)


def by_condition(runs: list[Run]) -> dict[tuple[int, tuple[str, str, str]], list[Run]]:
    grouped: dict = defaultdict(list)
    for run in runs:
        grouped[(run.full_run, run.condition)].append(run)
    return grouped


def integrity() -> list[str]:
    """Problems with the manifest: missing entries, hash mismatches, duplicates."""
    problems = []
    recorded: dict[str, str] = {}
    if MANIFEST.exists():
        for line in MANIFEST.read_text().splitlines():
            if not line.strip():
                continue
            digest, rel = line.split("  ", 1)
            if rel in recorded:
                problems.append(f"{rel}: listed twice in MANIFEST (a file was written twice)")
            recorded[rel] = digest
    skip = excluded()
    for path in sorted(RAW.glob("p*/*/*.jsonl")):
        rel = str(path.relative_to(RAW))
        if rel not in recorded and rel in skip:
            continue  # e.g. a run killed before it closed; documented in EXCLUDED.tsv
        if rel not in recorded:
            problems.append(f"{rel}: not in MANIFEST (run never closed, or file added by hand)")
        elif sha256(path) != recorded[rel]:
            problems.append(f"{rel}: content changed after its run closed")
    for rel in recorded:
        if not (RAW / rel).exists():
            problems.append(f"{rel}: in MANIFEST but the file is gone")
    return problems
