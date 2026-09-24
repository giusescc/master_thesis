"""P5 aggregator: what stays in a recipient's copy after the revoke, and what
does the recipient see that could tell it why? (HYPOTHESES.md, P5)

Variants: naive | 403-aware (see ch3/lib/aggregator.py; the 403-aware purge is
recipient-side logic we wrote, not a server feature).

    npm run exp:p5 [-- --config wac|acp] [--variant naive|403-aware] [--reps N] [--dry-run]
"""

from __future__ import annotations

import time

from ch3.lib import access, harness, scene
from ch3.lib.aggregator import Aggregator
from ch3.lib.agents import response_record
from ch3.lib.env import CH3, STATE

SYNC_INTERVAL_S, SYNCS_BEFORE, SYNCS_AFTER = 1.0, 3, 10
VOLATILE = {"date", "etag", "last-modified", "content-length", "keep-alive", "connection"}


def signature(rec: dict) -> dict:
    """What a recipient can compare between two refusals: status, body, stable headers."""
    headers = {k.lower(): v for k, v in rec["headers"].items() if k.lower() not in VOLATILE}
    return {"status": rec["status"], "body": rec.get("body", ""), "headers": dict(sorted(headers.items()))}


def run_one(log, config, variant, rep, rng) -> None:
    s = scene.build(log, config)
    stores = STATE / "stores"
    stores.mkdir(parents=True, exist_ok=True)
    agg = Aggregator(log, stores / f"{log.run_id}-p5-appr.sqlite", s.appr, [s.person, s.distractor], variant)

    # comparison probes, set up before the revoke
    never = s.container + "never.ttl"
    r = s.alice.put(never, (CH3 / "fixtures" / "distractor.ttl").read_text(), "text/turtle")
    access.set_readers(s.alice, never, [s.bob.web_id])  # appR is never granted
    log.write("probe_setup", probe="never_had_access", resource=never, put_status=r.status_code)
    gone = s.container + "scratch.ttl"
    s.alice.put(gone, (CH3 / "fixtures" / "distractor.ttl").read_text(), "text/turtle")
    access.set_readers(s.alice, gone, [s.appr.web_id, s.bob.web_id])
    log.write("probe_setup", probe="resource_deleted", resource=gone,
              appr_status_before_delete=s.appr.get(gone).status_code)

    for _ in range(SYNCS_BEFORE):
        agg.sync()
        time.sleep(SYNC_INTERVAL_S)
    rows_before = agg.rows(s.person)
    marks = scene.revoke(log, s, s.person, [s.bob.web_id])
    revoke_done = marks["done"]["t_ms"]

    first_after = None
    deleted_at = None
    for i in range(SYNCS_AFTER):
        statuses = agg.sync(full_response_for={s.person} if i == 0 else None)
        if i == 0:
            first_after = s.appr.get(s.person, headers={"accept": "text/turtle"})
        if variant == "403-aware" and deleted_at is None and agg.rows(s.person) == 0:
            deleted_at = log.t_ms()
        log.write("residual", source=s.person, rows=agg.rows(s.person), distractor_rows=agg.rows(s.distractor),
                  statuses=statuses)
        time.sleep(SYNC_INTERVAL_S)
    residual = agg.rows(s.person)
    distractor_rows = agg.rows(s.distractor)
    agg.close()

    revoked_rec = response_record(first_after, body=True)
    log.write("post_revoke_response", case="revoked", agent="appr", response=revoked_rec)
    never_rec = response_record(s.appr.get(never, headers={"accept": "text/turtle"}), body=True)
    log.write("post_revoke_response", case="never_had_access", agent="appr", response=never_rec)
    dr = s.alice.delete(gone)
    log.write("probe_delete", actor="alice", resource=gone, response=response_record(dr))
    gone_rec = response_record(s.appr.get(gone, headers={"accept": "text/turtle"}), body=True)
    log.write("post_revoke_response", case="resource_deleted", agent="appr", response=gone_rec)

    sig = {"revoked": signature(revoked_rec), "never": signature(never_rec), "deleted": signature(gone_rec)}
    log.write("refusal_signatures", **sig)
    log.summary(
        outcome={
            "rows_copied_before_revoke": rows_before > 0,
            "post_revoke_status": revoked_rec["status"],
            "residual_rows_after_10_syncs": residual > 0,
            "distractor_rows_kept": distractor_rows > 0,
            "status_never_had_access": never_rec["status"],
            "status_resource_deleted": gone_rec["status"],
            "revoked_vs_never_identical": sig["revoked"] == sig["never"],
            "revoked_vs_deleted_identical": sig["revoked"] == sig["deleted"],
            "refusal_header_names": sorted(sig["revoked"]["headers"]),
        },
        metrics={
            "rows_person_before": rows_before,
            "rows_person_residual": residual,
            "rows_distractor": distractor_rows,
            "revoke_to_row_deletion_ms": round(deleted_at - revoke_done, 1) if deleted_at else None,
        },
    )


if __name__ == "__main__":
    raise SystemExit(harness.main("p5", run_one))
