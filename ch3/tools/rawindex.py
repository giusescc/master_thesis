"""Read ``ch3/results/raw/`` back: runs by condition and full run, plus integrity."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass
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


def load_runs() -> list[Run]:
    runs = []
    for path in sorted(RAW.glob("p*/*/*.jsonl")):
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
        ))
    return runs


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
    for path in sorted(RAW.glob("p*/*/*.jsonl")):
        rel = str(path.relative_to(RAW))
        if rel not in recorded:
            problems.append(f"{rel}: not in MANIFEST (run never closed, or file added by hand)")
        elif sha256(path) != recorded[rel]:
            problems.append(f"{rel}: content changed after its run closed")
    for rel in recorded:
        if not (RAW / rel).exists():
            problems.append(f"{rel}: in MANIFEST but the file is gone")
    return problems
