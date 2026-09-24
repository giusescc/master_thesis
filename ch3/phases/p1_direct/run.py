"""P1 direct path: how fast does a revoke reach appR's own GETs? (HYPOTHESES.md, P1)

appR and bob poll ``person.ttl`` every 50 ms from 1 s before alice's revoke to
10 s after it. bob is the control.

    npm run exp:p1 [-- --config wac|acp] [--reps N] [--dry-run]
"""

from __future__ import annotations

import time

from ch3.lib import harness, scene
from ch3.lib.agents import response_record
from ch3.lib.poll import Poller

PRE_S, POST_S, INTERVAL_S = 1.0, 10.0, 0.05


def _wac_allow(rec: dict) -> str:
    return next((v for k, v in rec.get("headers", {}).items() if k.lower() == "wac-allow"), "<absent>")


def run_one(log, config, variant, rep, rng) -> None:
    s = scene.build(log, config)
    before = {}
    for agent in (s.appr, s.bob):
        r = agent.get(s.person)
        before[agent.name] = r
        log.write("read_before", agent=agent.name, response=response_record(r, body=True))
    token_before = s.appr.token_fingerprint()
    log.write("token", agent="appr", when="before", fingerprint=token_before)

    pollers = [Poller(log, s.appr, s.person, INTERVAL_S, body=True), Poller(log, s.bob, s.person, INTERVAL_S)]
    for p in pollers:
        p.start()
    time.sleep(PRE_S)
    marks = scene.revoke(log, s, s.person, [s.bob.web_id])
    revoke_done = marks["done"]["t_ms"]
    time.sleep(POST_S)
    for p in pollers:
        p.stop()
    for p in pollers:
        p.join()
    token_after = s.appr.token_fingerprint()
    log.write("token", agent="appr", when="after", fingerprint=token_after)

    appr, bob = pollers[0].records, pollers[1].records
    after = [r for r in appr if r["sent_t_ms"] > revoke_done]
    straddling = [r for r in appr if r["sent_t_ms"] <= revoke_done < r["recv_t_ms"]]
    denials = [r for r in after if r["status"] is None or not 200 <= r["status"] < 300]
    stale = [r for r in after if r["status"] is not None and 200 <= r["status"] < 300]
    ttd = round(denials[0]["recv_t_ms"] - revoke_done, 3) if denials else None
    deny_bodies = sorted({r.get("body", "") for r in denials})

    log.summary(
        outcome={
            "appr_before_status": before["appr"].status_code,
            "bob_before_status": before["bob"].status_code,
            "appr_after_statuses": sorted({r["status"] for r in after}, key=str),
            "appr_stale_read": bool(stale),
            "appr_denied": bool(denials),
            "bob_statuses": sorted({r["status"] for r in bob}, key=str),
            "appr_token_unchanged": token_before == token_after,
            "wac_allow_appr_before": before["appr"].headers.get("WAC-Allow", "<absent>"),
            "wac_allow_appr_after": sorted({_wac_allow(r) for r in after}),
            "wac_allow_bob": sorted({_wac_allow(r) for r in bob}),
            "deny_bodies": deny_bodies,
        },
        metrics={
            "time_to_denial_ms": ttd,
            "stale_reads": len(stale),
            "straddling_requests": [{"status": r["status"], "sent_t_ms": r["sent_t_ms"], "recv_t_ms": r["recv_t_ms"]} for r in straddling],
            "revoke_latency_ms": round(marks["done"]["t_ms"] - marks["sent"]["t_ms"], 3),
            "appr_requests": len(appr), "appr_requests_after": len(after), "bob_requests": len(bob),
            "skipped_slots": {"appr": pollers[0].skipped, "bob": pollers[1].skipped},
        },
    )


if __name__ == "__main__":
    raise SystemExit(harness.main("p1", run_one))
