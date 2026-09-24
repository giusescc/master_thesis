"""Summarise one phase's raw runs: distinct outcomes (with counts) and timing
distributions per condition. Used to write OBSERVATIONS.md; prints Markdown.

    uv run python -m ch3.tools.summarize p1 [--full-run 1]
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter

from ch3.lib.conditions import CONFIGS, VARIANTS
from ch3.tools.rawindex import by_condition, load_runs
from ch3.lib.jsonl import read_run


def pct(values: list[float], p: float) -> float:
    ordered = sorted(values)
    k = max(0, min(len(ordered) - 1, round(p / 100 * (len(ordered) - 1))))
    return ordered[k]


def numeric_metrics(runs) -> dict[str, list[float]]:
    out: dict[str, list[float]] = {}
    for run in runs:
        summary = next(l for l in read_run(run.path) if l["event"] == "summary")
        for key, value in summary.get("metrics", {}).items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                out.setdefault(key, []).append(float(value))
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase")
    parser.add_argument("--full-run", type=int, default=1)
    args = parser.parse_args()
    grouped = by_condition(load_runs())
    for config in CONFIGS:
        for variant in VARIANTS[args.phase]:
            runs = [r for r in grouped.get((args.full_run, (args.phase, config, variant)), []) if r.completed]
            print(f"### {args.phase}/{config}/{variant}: {len(runs)} completed runs\n")
            counts = Counter(json.dumps(r.outcome, sort_keys=True) for r in runs)
            for outcome, n in counts.most_common():
                print(f"- {n}× `{outcome}`")
            for key, values in numeric_metrics(runs).items():
                print(f"- {key}: median {statistics.median(values):.1f}, p95 {pct(values, 95):.1f}, "
                      f"min {min(values):.1f}, max {max(values):.1f} (n={len(values)})")
            files = sorted(str(r.path.relative_to(r.path.parents[2])) for r in runs)
            if files:
                print(f"- raw: `results/raw/{files[0].rsplit('/', 1)[0]}/` ({files[0].rsplit('/', 1)[1]} … {files[-1].rsplit('/', 1)[1]})")
            print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
