"""Record every HTTP exchange as citable evidence, with secrets redacted.

A thesis claim like "the server returned 403 after revocation" is only as good
as the transcript behind it.  Each experiment writes its exchanges to
``experiments/NN_name/evidence/`` in two forms:

* ``transcript.jsonl`` -- one JSON object per exchange, for machine analysis.
* ``transcript.md``    -- the same thing readable, for an appendix.

**Nothing secret is ever written.**  ``Authorization``, ``DPoP`` and cookie
headers are replaced with a placeholder before anything touches disk, because
these files are committed to a git repository.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

#: Headers whose values are secrets or bearer-equivalents.  Redacted always.
_SENSITIVE = {"authorization", "dpop", "cookie", "set-cookie"}

#: Headers worth keeping in the transcript: these are the ones the thesis
#: actually reasons about.
_INTERESTING = {
    "wac-allow",
    "link",
    "content-type",
    "location",
    "www-authenticate",
    "allow",
    "accept-patch",
    "etag",
}


def _redact(headers: Any) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in dict(headers).items():
        lower = key.lower()
        if lower in _SENSITIVE:
            out[key] = "<redacted>"
        elif lower in _INTERESTING:
            out[key] = value
    return out


class EvidenceLog:
    """Append-only record of HTTP exchanges for one experiment run."""

    def __init__(self, directory: Path | str, experiment: str) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.experiment = experiment
        self.entries: list[dict[str, Any]] = []
        self._jsonl = self.directory / "transcript.jsonl"
        self._md = self.directory / "transcript.md"
        # Truncate: a re-run replaces its own evidence, so the files on disk
        # always describe the most recent run rather than an accumulation.
        self._jsonl.write_text("")
        self._md.write_text(
            f"# Evidence transcript -- {experiment}\n\n"
            "Every HTTP exchange performed by this experiment, in order.\n"
            "Authorization and DPoP headers are redacted; they are secrets.\n\n"
        )

    def record(self, actor: str, response: requests.Response, note: str = "") -> None:
        """Record one request/response pair, attributed to the acting user."""
        request = response.request
        entry = {
            "n": len(self.entries) + 1,
            "at": datetime.now(tz=timezone.utc).isoformat(),
            "actor": actor,
            "method": request.method,
            "url": request.url,
            "status": response.status_code,
            "request_headers": _redact(request.headers),
            "response_headers": _redact(response.headers),
            "note": note,
        }
        self.entries.append(entry)

        with self._jsonl.open("a") as handle:
            handle.write(json.dumps(entry) + "\n")

        with self._md.open("a") as handle:
            handle.write(f"## {entry['n']}. {actor}: {entry['method']} {entry['url']}\n\n")
            if note:
                handle.write(f"*{note}*\n\n")
            handle.write(f"- **Status:** `{entry['status']}`\n")
            for key, value in entry["response_headers"].items():
                handle.write(f"- **{key}:** `{value}`\n")
            handle.write("\n")

    def summary(self) -> str:
        return f"{len(self.entries)} exchanges recorded in {self.directory}"
