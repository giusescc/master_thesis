# Context: Solid thesis lab

Domain terms used across the lab. `CLAUDE.md` holds the rules; this file holds the vocabulary.

## Chapter 2 (experiments/)

- **Enforced / Advertised / Declared only**: see `CLAUDE.md`. `WAC-Allow` is advertised, never "declared".

## Chapter 3: revocation half-life (ch3/)

- **Revocation half-life**: the study of what persists after alice revokes a recipient's access to a pod resource, where it persists, for how long, and whether any component receives a signal that access ended.
- **Recipient**: an agent that was granted read access and can hold copies. In Ch3, **appR** (an app with its own CSS account, WebID and client credentials) is revoked; **bob** is the control who keeps access, and later the second P7 recipient.
- **Phase**: one of P1–P7, each a separate script (`npm run exp:pN`).
- **Condition**: phase × server config (WAC on :3100, ACP on :3101) × variant (e.g. proxy A/B, engine a/a'/b, default/short channel expiry, naive/403-aware aggregator). Each condition gets at least 10 **repetitions**.
- **Time-to-denial**: time from the revoke write succeeding to appR's first non-2xx read (P1).
- **Residual**: data about the revoked resource that is still held by a recipient-side store after the revoke (proxy cache, Comunica cache, aggregator rows, retrieval-index chunks).
- **Deliberately permissive proxy configuration**: nginx config B (P2), which caches authenticated responses. Never call it "common": no source says so.
- **Withdrawal notice**: the P7 mitigation prototype. A JSON-LD message (ODRL + DPV terms) that alice POSTs to each recipient's LDN inbox on revoke. Recipients purge only if they cooperate; the mechanism cannot force that.
- **403-aware purge**: recipient-side logic we wrote for the P5 aggregator. It is not a server feature.
- **Identical results** (Ch3): two full runs give the same categorical outcome for every condition. Timings are reported as distributions, not compared for equality.
- **Observation vs interpretation**: `ch3/results/OBSERVATIONS.md` holds only measured facts, with no legal terms. Legal-facing notes go in `INTERPRETATION_NOTES.md`. Every claim is scoped as "CSS 7.2.0 with <config> did X".
