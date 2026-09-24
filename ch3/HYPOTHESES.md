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

## P2: HTTP caching (pre-registered before P2's first run, dry runs included)

**Proxy.** nginx 1.28.3 in Docker, pinned by digest (`config/nginx/IMAGE`).
Two proxy configurations, both written for this experiment. Neither is CSS
behaviour.
- **Config A** (`config/nginx/nginx-A.conf`): caching on, honours origin
  headers (no `proxy_cache_valid`, no `proxy_ignore_headers`). Ports
  :3180→WAC, :3181→ACP.
- **Config B** (`config/nginx/nginx-B.conf`), a **deliberately permissive
  configuration**: every 200 is stored for 60 s whatever the origin says, and
  `Vary` is ignored, so the cache key is the URL only (Authorization and DPoP
  are not in it). Ports :3182→WAC, :3183→ACP. It is not claimed to be common.

**Lab arrangement.** CSS checks the DPoP proof's `htu` against its own URL.
When appR and bob send a request to the proxy, their DPoP proof therefore
names the origin URL (`http://localhost:310x/...`). The proxy sends
`Host: localhost:310x` upstream.

**Procedure (per rep, fresh URLs, so no cache entry is shared between reps).**
Build the scene. appR GETs `person.ttl` directly (all headers logged). appR
GETs it through the proxy twice, then bob once. alice revokes appR. appR GETs
directly once. Then appR GETs through the proxy every 1 s for 70 s, logging
status, `X-Cache-Status`, `Age` and a sha256 of the body. An anonymous client
GETs through the proxy and directly, right after the revoke and at the end.
bob GETs through the proxy at the end.

**Conditions.** p2 × {wac, acp} × {proxyA, proxyB}, ≥ 10 reps each.

**Predictions.**
- **H2.1 (origin headers; both configs).** CSS 7.2.0 LDP responses to
  `person.ttl` carry **no `Cache-Control` and no `Expires`**. They carry
  `ETag`, `Last-Modified` and `Vary: Accept,Authorization,Origin`, plus
  `WAC-Allow` on WAC only (see P1). Source reading:
  `src/server/middleware/StaticAssetHandler.ts` is the only emitter of
  `cache-control`, for static assets. `Vary` comes from
  `config/http/middleware/handlers/constant-headers.json`.
- **H2.2 (config A).** The proxy never stores `person.ttl` (every
  `X-Cache-Status` is `MISS`). After the revoke, every proxied GET by appR
  returns 403 from the origin, so no cached copy is served. This matches the
  direct path.
- **H2.3 (config B).** appR's second pre-revoke GET is a `HIT`. After the
  revoke, proxied GETs by appR return **200 with the cached fixture body**
  (`X-Cache-Status: HIT`, body hash equal to the pre-revoke body) until the
  entry is 60 s old, counted from the first `MISS`. After that the proxy asks
  the origin again and appR gets 403. appR's direct GET right after the revoke
  is 403 (as in P1). So the "stale window" seen through the proxy is about
  60 s minus the time between caching and the revoke.
- **H2.4 (config B).** Because the key is URL-only, an **anonymous** client
  gets the cached 200 through the proxy after the revoke while the entry
  lives, while the same anonymous GET directly to CSS is 401.
- **H2.5 (both).** bob, the control, gets 200 through the proxy throughout.
- **H2.6 (config B).** CSS sends no signal to the proxy when the ACL/ACR
  changes. The proxy has no way to learn of the revoke except by expiry.
  Nothing is observed that invalidates the entry early.
