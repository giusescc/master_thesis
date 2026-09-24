"""Run one phase over its conditions: ``--config``, ``--variant``, ``--reps``.

Each repetition gets its own RunLog. An exception inside a run is written to
that run's file as ``run_error`` (with the traceback) and the run is counted as
failed by ``exp:check``; the harness moves on rather than retrying, so a flaky
condition shows up in the evidence instead of being hidden.

``--dry-run`` writes to ``ch3/results/scratch/`` (git-ignored), never counted.
"""

from __future__ import annotations

import argparse
import random
import traceback
from typing import Callable

from ch3.lib.conditions import CONFIGS, MIN_REPS, VARIANTS
from ch3.lib.env import SEED
from ch3.lib.jsonl import RunLog

RunFn = Callable[[RunLog, str, str, int, random.Random], None]


def main(phase: str, run_one: RunFn, before_variant: Callable[[str, str], None] | None = None,
         after_variant: Callable[[str, str], None] | None = None) -> int:
    parser = argparse.ArgumentParser(prog=f"exp:{phase}")
    parser.add_argument("--config", choices=[*CONFIGS, "all"], default="all")
    parser.add_argument("--variant", choices=[*VARIANTS[phase], "all"], default="all")
    parser.add_argument("--reps", type=int, default=MIN_REPS)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    configs = CONFIGS if args.config == "all" else (args.config,)
    variants = VARIANTS[phase] if args.variant == "all" else (args.variant,)
    failures = 0
    for config in configs:
        for variant in variants:
            if before_variant:
                before_variant(config, variant)
            try:
                for rep in range(1, args.reps + 1):
                    log = RunLog(phase, config, variant, rep, scratch=args.dry_run)
                    rng = random.Random(SEED + rep)
                    status = "ok"
                    try:
                        run_one(log, config, variant, rep, rng)
                    except Exception as exc:  # noqa: BLE001 -- recorded in evidence
                        failures += 1
                        status = "error"
                        log.write("run_error", error=type(exc).__name__, message=str(exc),
                                  traceback=traceback.format_exc())
                    finally:
                        log.close()
                    print(f"  {phase}/{config}/{variant} rep {rep:02d}: {status}  {log.path.name}", flush=True)
            finally:
                if after_variant:
                    after_variant(config, variant)
    print(f"{phase}: done, {failures} failed run(s)")
    return 1 if failures else 0
