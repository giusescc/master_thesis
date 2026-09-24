# Chapter 3: pre-registered hypotheses

Each phase's section is committed **in its own commit, before that phase's
first real run** (CLAUDE.md rule 3). `git log -- ch3/HYPOTHESES.md` is the
evidence that no prediction was written after the results. If a prediction
turns out wrong, the section is left as written, and the correction is
recorded in `results/OBSERVATIONS.md` with the reason.

Scope of every prediction: **CSS 7.2.0**, config `ch3/config/css-wac.json`
(WAC, file backend) on :3100 or `ch3/config/css-acp.json` (ACP, file backend)
on :3101, both with the notification components of
`css:config/http/notifications/all.json`. Predictions labelled
"source reading" come from reading the CSS v7.2.0 source. They are
predictions, not results.

Agents: **alice** owns the pod. **appR** is the recipient whose Read is
revoked. **bob** is the control, who keeps Read on `person.ttl` in P1–P6.
Each run uses a fresh container `/alice/ch3/<run-id>/` holding `person.ttl`
(the fixture, which gets revoked) and `distractor.ttl` (appR keeps Read on it).

## P1: direct path (pre-registered before P1's first run)

**Procedure.** Build the scene (appR and bob can read `person.ttl`). appR and
bob each GET `person.ttl` once (the "before" read). appR and bob then each
start polling `person.ttl` with GET every 50 ms, on independent schedules
(one thread each). Polling starts 1 s before the revoke and ends 10 s after it.
alice revokes appR (WAC: PUT the resource's `.acl` naming only alice and bob;
ACP: PUT the resource's `.acr` naming only bob). Every request is logged with
its send time, response time, status code and full (redacted) headers.

**Definitions.** `revoke_done` = when alice's revoke response arrived.
*Time-to-denial* = response time of appR's first non-2xx whose request was
**sent after** `revoke_done`, minus `revoke_done`. A *stale read* = a 2xx to
appR whose request was sent after `revoke_done`. Requests in flight across
`revoke_done` are logged but belong to neither category.

**Conditions.** p1 × {wac, acp} × {direct}, ≥ 10 reps each.

**Predictions.**

- **H1.1 (both configs).** appR gets 200 before the revoke, and **403** on
  every request sent after `revoke_done` (403, not 401, because appR is
  authenticated). No stale reads. Time-to-denial is therefore bounded by one
  polling interval plus one request latency (≤ ~60 ms). Source reading:
  `src/authorization/WebAclReader.ts` and `AcpReader.ts` read the access
  document on every request, and `src/authorization/` has no permission cache.
- **H1.2 (both configs).** bob, the control, gets 200 on every request before,
  during and after the revoke.
- **H1.3.** Denial happens without appR's access token changing. appR keeps
  one token throughout (logged by its `jti`-free fingerprint: the token's
  `exp` claim is unchanged). The server decides on the access document, not
  the token.
- **H1.4 (WAC).** The `WAC-Allow` header on appR's 200 responses before the
  revoke advertises `user="read"`. On appR's 403 responses after the revoke,
  it is absent or does not advertise read.
- **H1.5 (ACP).** No `WAC-Allow` header on any response. *Honesty note:* this
  was already seen incidentally in the Chunk 1 smoke test (one request per
  agent), so it is a confirmation, not a blind prediction.
- **H1.6.** The 403 body and headers carry nothing that says *why* access was
  denied (e.g. nothing distinguishing "revoked" from "never granted"). P5
  tests this distinction directly.
