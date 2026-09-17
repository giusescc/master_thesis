"""Write an experiment's outcome back into its README and a machine-readable file.

Each experiment README is written *before* the run and contains the hypotheses.
After the run, everything below the ``## Result`` heading is replaced with the
observed table and a plain-language summary. The hypotheses above it are never
touched, so the README always shows prediction and outcome side by side.

``result.json`` carries the same data for ``pytest`` and for RESULTS.md.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from solidlib.checks import CheckTable, Status

RESULT_HEADING = "## Result"


def write_result(experiment_dir: Path | str, table: CheckTable, summary: str) -> Path:
    directory = Path(experiment_dir)
    readme = directory / "README.md"

    body = [
        RESULT_HEADING,
        "",
        f"_Last run: {datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}._",
        "",
        table.to_markdown(),
        "",
        "### In plain language",
        "",
        summary.strip(),
        "",
        "Raw HTTP evidence for every row above: [`evidence/transcript.md`](evidence/transcript.md)",
        "(and `evidence/transcript.jsonl` for machine analysis).",
        "",
    ]

    text = readme.read_text()
    head = text.split(RESULT_HEADING)[0].rstrip() if RESULT_HEADING in text else text.rstrip()
    readme.write_text(head + "\n\n" + "\n".join(body))

    payload = {
        "experiment": table.experiment,
        "ran_at": datetime.now(tz=timezone.utc).isoformat(),
        "checks": [
            {
                "name": c.name,
                "expected": str(c.expected),
                "actual": str(c.actual),
                "advertised": c.advertised,
                "status": str(c.status),
                "note": c.note,
            }
            for c in table.checks
        ],
        "unexpected": len(table.unexpected),
        "summary": summary.strip(),
    }
    result_path = directory / "result.json"
    result_path.write_text(json.dumps(payload, indent=2) + "\n")
    return result_path


def finish(experiment_dir: Path | str, table: CheckTable, summary: str) -> int:
    """Print the table, persist the result, and return a shell exit code.

    A non-zero exit when anything is ``UNEXPECTED`` is what makes ``pytest``
    fail and what stops the build for review.
    """
    print(table.render())
    write_result(experiment_dir, table, summary)
    if table.unexpected:
        print(
            "\nStopping: at least one stated expectation did not hold. "
            "This is a finding, not a bug to paper over -- review before continuing."
        )
        return 1
    return 0
