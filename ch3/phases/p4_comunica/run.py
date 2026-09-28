"""P4 Comunica link traversal: does a query engine that read the fixture before
the revoke still answer from it afterwards? (HYPOTHESES.md, P4)

Variants:  a             same engine instance, default settings
           a-invalidate  same engine instance, invalidateHttpCache() before the second query
           b             a fresh engine instance for the second query

    npm run exp:p4 [-- --config wac|acp] [--variant a|a-invalidate|b] [--reps N] [--dry-run]
"""

from __future__ import annotations

import json
import os
import subprocess

from ch3.lib import harness, scene
from ch3.lib.env import CH3, identity

DRIVER = CH3 / "phases" / "p4_comunica" / "driver.mjs"

QUERY = """PREFIX schema: <https://schema.org/>
SELECT ?person ?name ?job WHERE { ?person schema:name ?name ; schema:jobTitle ?job . }"""


class Driver:
    def __init__(self, log, config: str) -> None:
        ident = identity(config, "appr")
        env = {**os.environ, "CH3_ISSUER": ident.issuer, "CH3_CLIENT_ID": ident.client_id,
               "CH3_CLIENT_SECRET": ident.client_secret}
        self.log = log
        self.proc = subprocess.Popen(["node", str(DRIVER)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True, env=env, cwd=DRIVER.parent)
        self.n = 0

    def send(self, cmd: str, **fields) -> tuple[dict, list[dict]]:
        self.n += 1
        msg = {"id": self.n, "cmd": cmd, **fields}
        self.log.write("comunica_command", **msg)
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()
        http = []
        while True:
            line = self.proc.stdout.readline()
            if not line:
                raise RuntimeError(f"driver exited: {self.proc.stderr.read()[-2000:]}")
            event = json.loads(line)
            node_ts = event.pop("ts")
            if event["event"] == "http":
                http.append(event)
                self.log.write("comunica_http", node_ts=node_ts, **{k: v for k, v in event.items() if k != "event"})
            elif event["event"] == "reply" and event["id"] == self.n:
                self.log.write("comunica_reply", node_ts=node_ts, **{k: v for k, v in event.items() if k != "event"})
                return event, http

    def close(self) -> None:
        try:
            self.send("exit")
        except Exception:  # noqa: BLE001
            pass
        self.proc.wait(timeout=10)


def _names(reply: dict) -> list[str]:
    return sorted({row.get("name") for row in reply.get("rows", [])}) if reply.get("ok") else []


def _person_requests(http: list[dict], person: str) -> list[int]:
    return [h["status"] for h in http if h["url"].split("#")[0] == person]


def run_one(log, config, variant, rep, rng) -> None:
    s = scene.build(log, config)
    sources = [s.container]
    driver = Driver(log, config)
    try:
        driver.send("new", engine="e1")
        before, http_before = driver.send("query", engine="e1", query=QUERY, sources=sources)
        scene.revoke(log, s, s.person, [s.bob.web_id])
        direct = s.appr.get(s.person).status_code
        log.write("direct_after", agent="appr", status=direct)
        engine = "e1"
        if variant == "a-invalidate":
            driver.send("invalidate", engine="e1")
        elif variant == "b":
            driver.send("new", engine="e2")
            engine = "e2"
        after, http_after = driver.send("query", engine=engine, query=QUERY, sources=sources)
    finally:
        driver.close()

    log.summary(
        outcome={
            "before_ok": before["ok"],
            "before_names": _names(before),
            "direct_after_status": direct,
            "after_ok": after["ok"],
            "after_error_name": after.get("error_name"),
            "after_names": _names(after),
            "after_includes_revoked_person": "Tesmer Quillon" in _names(after),
            "after_person_ttl_requests": sorted(set(_person_requests(http_after, s.person))),
            "after_made_http_requests": bool(http_after),
        },
        metrics={
            "http_before": len(http_before),
            "http_after": len(http_after),
            "after_error": after.get("error"),
        },
    )


if __name__ == "__main__":
    raise SystemExit(harness.main("p4", run_one))
