"""The four-state result model used by every experiment.

Why not PASS/FAIL
-----------------
The research question is not "did the code work" but "what does the server
actually enforce".  PASS/FAIL flattens exactly the distinction the thesis is
about: an ODRL prohibition having no effect is a *correct prediction* and the
most interesting negative result in the project.  So each check declares what it
**expects** before running, and is classified as:

``ENFORCED``
    The server changed its behaviour because of the rule under test.
``DECLARED-ONLY``
    The statement exists as metadata and demonstrably changed nothing.
``NOT-SUPPORTED``
    The server or the specification provides no mechanism at all.
``UNEXPECTED``
    Reality disagreed with the stated expectation.

``UNEXPECTED`` is the point of the design.  It is assigned automatically
whenever ``actual != expected``, so a surprising result can never be quietly
absorbed into a friendlier category -- it shouts, and the run stops.

Note on vocabulary: the ``WAC-Allow`` header is recorded separately as
**advertised permissions**.  It is not "declared only" -- the server is
truthfully announcing rules it does enforce.  Conflating the two would blur the
central claim, so advertised permissions get their own column.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Status(str, Enum):
    ENFORCED = "ENFORCED"
    DECLARED_ONLY = "DECLARED-ONLY"
    NOT_SUPPORTED = "NOT-SUPPORTED"
    UNEXPECTED = "UNEXPECTED"

    def __str__(self) -> str:  # pragma: no cover - display only
        return self.value


@dataclass
class Check:
    name: str
    expected: Any
    actual: Any
    status: Status
    advertised: str | None = None
    note: str = ""

    @property
    def matched(self) -> bool:
        return self.status is not Status.UNEXPECTED


@dataclass
class CheckTable:
    """Collects checks and renders the result table an experiment prints."""

    experiment: str
    checks: list[Check] = field(default_factory=list)

    def check(
        self,
        name: str,
        expected: Any,
        actual: Any,
        on_match: Status,
        advertised: str | None = None,
        note: str = "",
    ) -> Check:
        """Record one check.

        ``on_match`` is the classification to use *if the expectation holds*.
        If it does not, the check is ``UNEXPECTED`` regardless of what was hoped
        for -- the expectation cannot be revised after seeing the result.
        """
        status = on_match if actual == expected else Status.UNEXPECTED
        result = Check(
            name=name,
            expected=expected,
            actual=actual,
            status=status,
            advertised=advertised,
            note=note,
        )
        self.checks.append(result)
        return result

    @property
    def unexpected(self) -> list[Check]:
        return [c for c in self.checks if c.status is Status.UNEXPECTED]

    def render(self) -> str:
        """Render a fixed-width table for the terminal."""
        headers = ("#", "Check", "Expected", "Actual", "Advertised (WAC-Allow)", "Result")
        rows = [
            (
                str(i),
                c.name,
                str(c.expected),
                str(c.actual),
                c.advertised or "-",
                str(c.status),
            )
            for i, c in enumerate(self.checks, start=1)
        ]
        widths = [
            max(len(headers[col]), *(len(row[col]) for row in rows)) if rows else len(headers[col])
            for col in range(len(headers))
        ]
        line = "  ".join("-" * w for w in widths)
        out = [
            f"\n{self.experiment}",
            line,
            "  ".join(h.ljust(w) for h, w in zip(headers, widths)),
            line,
        ]
        out.extend("  ".join(v.ljust(w) for v, w in zip(row, widths)) for row in rows)
        out.append(line)

        counts: dict[str, int] = {}
        for c in self.checks:
            counts[str(c.status)] = counts.get(str(c.status), 0) + 1
        out.append("  ".join(f"{k}: {v}" for k, v in sorted(counts.items())))
        if self.unexpected:
            out.append("")
            out.append("!! UNEXPECTED results -- a stated expectation did not hold:")
            for c in self.unexpected:
                out.append(f"   - {c.name}: expected {c.expected!r}, got {c.actual!r}")
        return "\n".join(out)

    def to_markdown(self) -> str:
        """Render the same table as Markdown for the experiment README/RESULTS."""
        out = [
            "| # | Check | Expected | Actual | Advertised (`WAC-Allow`) | Result |",
            "|---|---|---|---|---|---|",
        ]
        for i, c in enumerate(self.checks, start=1):
            advertised = f"`{c.advertised}`" if c.advertised else "—"
            out.append(
                f"| {i} | {c.name} | `{c.expected}` | `{c.actual}` | {advertised} | **{c.status}** |"
            )
        return "\n".join(out)
