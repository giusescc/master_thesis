"""``npm run exp:check``: is the raw evidence complete and well-formed?

Exit 0 only if, for every full run present, every condition in
``ch3/lib/conditions.py`` has at least MIN_REPS completed runs, every line of
every raw file has an ISO 8601 UTC timestamp with milliseconds, every file
still matches the hash recorded when its run closed, and no counted run
spanned a system suspend (wall clock vs monotonic clock, see rawindex).
"""

from __future__ import annotations

import sys

from ch3.lib.conditions import MIN_REPS, conditions
from ch3.tools.rawindex import SUSPEND_THRESHOLD_S, by_condition, excluded, integrity, load_runs


def main() -> int:
    runs = load_runs()
    grouped = by_condition(runs)
    full_runs = sorted({r.full_run for r in runs}) or [1]
    problems: list[str] = []

    print(f"{'full run':>8}  {'condition':<30} {'completed':>9} {'failed':>6}")
    for fr in full_runs:
        for cond in conditions():
            group = grouped.get((fr, cond), [])
            done = sum(r.completed for r in group)
            failed = len(group) - done
            flag = "" if done >= MIN_REPS else f"  <-- needs {MIN_REPS}"
            print(f"{fr:>8}  {'/'.join(cond):<30} {done:>9} {failed:>6}{flag}")
            if done < MIN_REPS:
                problems.append(f"full run {fr}, {'/'.join(cond)}: {done} completed runs (< {MIN_REPS})")

    for run in runs:
        if run.bad_ts_lines:
            problems.append(f"{run.path.name}: lines without a valid ISO-ms-UTC ts: {run.bad_ts_lines[:10]}")
        if run.suspended_s > SUSPEND_THRESHOLD_S:
            problems.append(f"{run.path.relative_to(run.path.parents[2])}: spanned a system suspend "
                            f"({run.suspended_s} s of wall clock not seen by the monotonic clock); "
                            "exclude it in raw/EXCLUDED.tsv and run a make-up rep")
    problems += integrity()
    skipped = excluded()
    if skipped:
        print(f"\n{len(skipped)} raw file(s) kept but excluded from counting (raw/EXCLUDED.tsv):")
        for rel, reason in skipped.items():
            print(f"  - {rel}: {reason}")

    if problems:
        print(f"\nexp:check FAILED ({len(problems)} problem(s)):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"\nexp:check OK: {len(runs)} raw files, every condition has >= {MIN_REPS} completed runs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
