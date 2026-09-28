"""A small recipient-side aggregator: copies what an agent can read into SQLite.

Used by P5 (the baseline) and P7 (whose withdrawal notice asks the recipient to
purge it). Two sync policies:

* ``naive``      a failed fetch changes nothing; rows already copied stay.
* ``403-aware``  a fetch that now fails (non-2xx) deletes that source's rows.
                 This is recipient-side logic WE wrote for the experiment. It is
                 not a CSS or Solid feature, and the server does not ask for it.

One row per RDF triple, with the source URL it came from.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import rdflib

from ch3.lib.agents import Agent, response_record
from ch3.lib.jsonl import RunLog, utc_ms

SCHEMA = """CREATE TABLE IF NOT EXISTS triples (
    source TEXT NOT NULL, subject TEXT NOT NULL, predicate TEXT NOT NULL, object TEXT NOT NULL,
    copied_at TEXT NOT NULL)"""


class Aggregator:
    def __init__(self, log: RunLog, db_path: Path, agent: Agent, sources: list[str], policy: str) -> None:
        assert policy in ("naive", "403-aware")
        self.log, self.agent, self.sources, self.policy = log, agent, sources, policy
        self.db = sqlite3.connect(db_path, check_same_thread=False)
        self.db.execute(SCHEMA)
        self.db.commit()
        self.db_path = db_path

    def rows(self, source: str | None = None) -> int:
        if source is None:
            return self.db.execute("SELECT COUNT(*) FROM triples").fetchone()[0]
        return self.db.execute("SELECT COUNT(*) FROM triples WHERE source = ?", (source,)).fetchone()[0]

    def purge(self, source: str) -> int:
        n = self.db.execute("DELETE FROM triples WHERE source = ?", (source,)).rowcount
        self.db.commit()
        return n

    def sync(self, full_response_for: set[str] | None = None) -> dict[str, int]:
        """Fetch every source once; returns {source: status}."""
        statuses = {}
        for url in self.sources:
            r = self.agent.get(url, headers={"accept": "text/turtle"})
            statuses[url] = r.status_code
            action = "none"
            if r.ok:
                graph = rdflib.Graph().parse(data=r.text, format="turtle", publicID=url)
                now = utc_ms()
                with self.db:
                    self.db.execute("DELETE FROM triples WHERE source = ?", (url,))
                    self.db.executemany("INSERT INTO triples VALUES (?, ?, ?, ?, ?)",
                                        [(url, s.n3(), p.n3(), o.n3(), now) for s, p, o in graph])
                action = "copied"
            elif self.policy == "403-aware":
                deleted = self.purge(url)
                action = f"deleted {deleted} rows"
            record = response_record(r, body=bool(full_response_for and url in full_response_for))
            self.log.write("aggregator_sync", agent=self.agent.name, policy=self.policy, source=url,
                           status=r.status_code, action=action, rows_now=self.rows(url),
                           response=record)
        return statuses

    def close(self) -> None:
        self.db.close()
