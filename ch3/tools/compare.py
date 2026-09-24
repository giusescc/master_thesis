"""``npm run exp:compare``: do two full runs give the same categorical outcomes?

"Identical results" for Chapter 3 (CONTEXT.md) means: for every condition, the
set of distinct categorical ``outcome`` values in full run 1 equals the set in
full run 2. Timings live in ``metrics`` and are never compared for equality.

Exit 0 only if both full runs are present, every condition matches, and no raw
file was overwritten or modified (manifest check).
"""

from __future__ import annotations

import json
import sys

from ch3.lib.conditions import conditions
from ch3.tools.rawindex import by_condition, integrity, load_runs


def outcome_set(runs) -> set[str]:
    return {json.dumps(r.outcome, sort_keys=True) for r in runs if r.completed}


def main() -> int:
    grouped = by_condition(load_runs())
    problems: list[str] = []
    for cond in conditions():
        name = "/".join(cond)
        one, two = outcome_set(grouped.get((1, cond), [])), outcome_set(grouped.get((2, cond), []))
        if not one or not two:
            problems.append(f"{name}: missing completed runs in full run {'1' if not one else '2'}")
            print(f"MISSING  {name}")
        elif one == two:
            print(f"SAME     {name}  ({len(one)} distinct outcome(s))")
        else:
            problems.append(f"{name}: outcomes differ")
            print(f"DIFFERS  {name}")
            for label, only in (("only in run 1", one - two), ("only in run 2", two - one)):
                for o in sorted(only):
                    print(f"           {label}: {o}")
    problems += integrity()
    if problems:
        print(f"\nexp:compare FAILED ({len(problems)} problem(s)):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("\nexp:compare OK: identical categorical outcomes per condition; no raw file overwritten.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
