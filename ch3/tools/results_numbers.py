"""Every number in ``ch3/results/RESULTS.md``'s one-table answer, recomputed
from the raw JSONL. Prints the table as Markdown, plus the coverage lines
(full runs, counted runs, exclusions) that RESULTS.md states.

    uv run python -m ch3.tools.results_numbers

Counted runs are those ``exp:check`` counts: raw files not listed in
``raw/EXCLUDED.tsv``, completed (summary line, no run_error). Categorical
facts are taken over the counted runs of **both** full runs and shown as
"value" when every run agrees, else as "value ×n; value ×m". Timings come from
**full run 1 only**, as in OBSERVATIONS.md: median (min–max).

The "Status" column is our reading of each row in the CLAUDE.md vocabulary
(Enforced / Advertised / Declared only), fixed in STATUS below. It is not
computed; everything else is.
"""

from __future__ import annotations

import json
import statistics
from collections import Counter

from ch3.lib.conditions import CONFIGS, VARIANTS
from ch3.lib.jsonl import read_run
from ch3.tools.rawindex import by_condition, excluded, load_runs


def summary(run) -> dict:
    return next(l for l in read_run(run.path) if l["event"] == "summary")


def agreed(values: list) -> str:
    counts = Counter(json.dumps(v) if not isinstance(v, str) else v for v in values)
    if len(counts) == 1:
        return next(iter(counts))
    return "; ".join(f"{v} ×{n}" for v, n in counts.most_common())


def timing(values: list) -> str:
    values = [float(v) for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]
    if not values:
        return "n/a"
    return f"{statistics.median(values):.1f} ({min(values):.1f}–{max(values):.1f})"


def count_true(d: dict) -> int:
    return sum(1 for v in d.values() if v is True)


# phase -> (facts over both full runs, timings over full run 1)
# Each fact: (label, fn(outcome, metrics) -> value). Each timing: (label, metric key).
FACTS = {
    "p1": [
        ("stale reads after revoke_done", lambda o, m: m["stale_reads"]),
        ("appR statuses after the revoke", lambda o, m: o["appr_after_statuses"]),
        ("bob (control) statuses", lambda o, m: o["bob_statuses"]),
        ("`WAC-Allow` for appR before → after", lambda o, m: f"{o['wac_allow_appr_before']} → {o['wac_allow_appr_after'][0]}"),
    ],
    "p2": [
        ("appR's proxied 200s after the revoke (of polls)", lambda o, m: f"{m['stale_reads']} of {m['polls']}"),
        ("anonymous GET via proxy just after the revoke", lambda o, m: o["anon_proxy_after_early"]),
        ("anonymous GET direct to CSS", lambda o, m: o["anon_direct_after_status"]),
        ("origin `Cache-Control`", lambda o, m: o["origin_cache_control"]),
    ],
    "p3": [],  # split below: lifecycle vs unsubscribe variants
    "p4": [
        ("HTTP requests, 2nd query", lambda o, m: m["http_after"]),
        ("2nd query ok / rows", lambda o, m: f"{json.dumps(o['after_ok'])} / {len(o['after_names'])}"),
        ("`person.ttl` statuses in 2nd query", lambda o, m: o["after_person_ttl_requests"]),
    ],
    "p5": [
        ("`person.ttl` rows before → after 10 syncs", lambda o, m: f"{m['rows_person_before']} → {m['rows_person_residual']}"),
        ("distractor rows", lambda o, m: m["rows_distractor"]),
        ("withdrawn = never granted = deleted (status, body, headers)",
         lambda o, m: f"{o['post_revoke_status']}/{o['status_never_had_access']}/{o['status_resource_deleted']}, "
                      f"identical: {json.dumps(o['revoked_vs_never_identical'] and o['revoked_vs_deleted_identical'])}"),
    ],
    "p6": [
        ("`person.ttl` chunks in memory after the revoke", lambda o, m: o["chunks_from_revoked_after"]),
        ("questions with top-1 from `person.ttl` (of 10)", lambda o, m: count_true(o["after_top1_from_revoked"])),
        ("generated answers correct after the revoke (of 10)", lambda o, m: m["generation_correct_after"]),
        ("appR direct GET after the revoke", lambda o, m: o["direct_after_status"]),
    ],
    "p7": [
        ("residual `person.ttl` rows / chunks (appR, bob)",
         lambda o, m: ", ".join(f"{r['rows_person']}/{r['chunks_person']}" for r in o["recipients"].values())),
        ("questions still top-1 from `person.ttl` (appR, bob)",
         lambda o, m: ", ".join(str(r["questions_top1_from_revoked"]) for r in o["recipients"].values())),
        ("alice's POST / GET Location / GET inbox (appR)",
         lambda o, m: "/".join(str(o["alice_view"]["appr"].get(k)) for k in ("post_status", "get_location_status", "get_inbox_status"))),
        ("recipient list from alice's own grant log only", lambda o, m: o["recipient_list_from_own_grant_log"]),
        ("consent status read back (appR, bob)",
         lambda o, m: ", ".join(json.dumps(r["notice_has_consent_status"]) if "notice_has_consent_status" in r else "n/a (v1)" for r in o["recipients"].values())),
    ],
}
P3_LIFECYCLE = [
    ("notifications after the revoke, WS / Webhook (of 20)",
     lambda o, m: f"{o['after_revoke_notifications']['ws-person']} / {o['after_revoke_notifications']['hook-person']}"),
    ("any ACL/ACR-change signal", lambda o, m: o["acl_change_signal_in_window"] or o["any_message_mentions_acl_or_acr"]),
    ("reconnect to old `receiveFrom` receives", lambda o, m: o["reconnect_after_revoke_receives"]),
    ("new subscription on `person.ttl` (WS/Webhook)",
     lambda o, m: f"{o['new_subscription_status_after_revoke']['new-ws-person']}/{o['new_subscription_status_after_revoke']['new-hook-person']}"),
    ("advertised `endAt` (min)", lambda o, m: o["end_at_minutes"]["ws-person"]),
]
P3_UNSUB = [
    ("`DELETE <channel id>` status", lambda o, m: o["unsubscribe_status"]),
    ("received after the DELETE", lambda o, m: o["received_after_unsub"]),
    ("alice finds the channel without its id",
     lambda o, m: any(v[1] for k, v in o["alice_discovery"].items() if isinstance(v, list)) if "alice_discovery" in o else "n/a"),
]
TIMINGS = {
    "p1": [("time-to-denial (ms)", "time_to_denial_ms")],
    "p2": [("stale window (ms)", "stale_window_ms"), ("first proxied 403 (ms)", "first_denied_after_revoke_ms")],
    "p3": [],
    "p4": [],
    "p5": [("revoke → rows deleted (ms)", "revoke_to_row_deletion_ms")],
    "p6": [],
    "p7": [("notice sent → received, appR (ms)", "appr_sent_to_received_ms"),
           ("sent → purge done, appR (ms)", "appr_sent_to_purged_ms")],
}
# Our reading of the revoke on each path, in the CLAUDE.md vocabulary. Not computed.
STATUS = {
    "p1": "Revoke **Enforced** at once, per request; `WAC-Allow` **Advertised** on WAC only",
    "p2/proxyA": "Revoke **Enforced** (the proxy stored nothing)",
    "p2/proxyB": "Revoke **not enforced** on the proxy's copy (~60 s, anonymous too)",
    "p3/lifecycle": "**Enforced** for new subscriptions; **not enforced** on existing channels",
    "p3/unsub": "No owner-side control: a channel ends by `DELETE` with its id, from anyone",
    "p4": "Revoke **Enforced** (the engine re-requested)",
    "p5/naive": "Revoke **not enforced** on the copy",
    "p5/403-aware": "Revoke **not enforced** on the copy; recipient code deleted it on the 403",
    "p6": "Revoke **not enforced** on the memory",
    "p7/cooperating": "Notice **Declared only**; recipient code deleted the copies",
    "p7/non-cooperating": "Notice **Declared only**; copies kept; alice's view identical",
}


def status_for(phase: str, variant: str) -> str:
    if phase == "p3":
        return STATUS["p3/unsub" if variant.startswith("unsub") else "p3/lifecycle"]
    if phase == "p7":
        return STATUS["p7/non-cooperating" if variant.startswith("non") else "p7/cooperating"]
    return STATUS.get(f"{phase}/{variant}", STATUS.get(phase, ""))


def main() -> int:
    runs = load_runs()
    grouped = by_condition(runs)
    full_runs = sorted({r.full_run for r in runs})
    print("| Phase | Config | Variant | Counted runs (full run 1 + 2) | Distinct outcomes | "
          "Observed (all counted runs) | Timing, full run 1: median (min–max) | Status |")
    print("|---|---|---|---|---|---|---|---|")
    for phase, variants in VARIANTS.items():
        for variant in variants:
            for config in CONFIGS:
                per_fr = {fr: [r for r in grouped.get((fr, (phase, config, variant)), []) if r.completed]
                          for fr in full_runs}
                counted = [r for rs in per_fr.values() for r in rs]
                sums = [summary(r) for r in counted]
                facts = FACTS[phase] or (P3_UNSUB if variant.startswith("unsub") else P3_LIFECYCLE)
                observed = "; ".join(
                    f"{label}: {agreed([fn(s['outcome'], s.get('metrics', {})) for s in sums])}" for label, fn in facts)
                fr1 = [summary(r) for r in per_fr.get(1, [])]
                timings = "; ".join(f"{label}: {timing([s['metrics'].get(key) for s in fr1])}"
                                    for label, key in TIMINGS[phase]) or "—"
                distinct = len({json.dumps(r.outcome, sort_keys=True) for r in counted})
                runs_col = " + ".join(str(len(per_fr[fr])) for fr in full_runs)
                print(f"| {phase.upper()} | {config.upper()} | {variant} | {runs_col} | {distinct} | "
                      f"{observed} | {timings} | {status_for(phase, variant)} |")
    failed = sum(1 for r in runs if not r.completed)
    print(f"\nCoverage: full runs {full_runs}; {len(runs)} counted raw files "
          f"({len(runs) - failed} completed, {failed} failed); {len(excluded())} raw files excluded "
          f"(raw/EXCLUDED.tsv).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
