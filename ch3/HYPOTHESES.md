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

## P3: notifications (pre-registered before P3's first run, dry runs included)

**Setup.** CSS 7.2.0 advertises two subscription services in the storage
description (`/<pod>/.well-known/solid`): WebSocketChannel2023 and
WebhookChannel2023 (checked read-only before writing this). appR subscribes
with its own DPoP credentials. Its WebSocket client is Python `websockets`
15.0.1. Its webhook receiver is a local HTTP server on 127.0.0.1 that logs
every request in full (the `Authorization`/`DPoP` values are redacted, but
the decoded claims of the token CSS sends are logged, without the signature).

**Procedure, variants `default` and `short`.** Build the scene. appR opens
four channels: WebSocket and Webhook on `person.ttl`, and WebSocket and
Webhook on the run container. Each subscription response is logged in full.
appR connects to both `receiveFrom` URLs. alice modifies `person.ttl` once
(a baseline, to show the channels work). alice revokes appR. For 3 s nothing
else happens (the window in which an ACL/ACR-change signal would arrive).
Then alice modifies `person.ttl` 20× at 1 s intervals (N3 Patch, one inserted
triple each). After that:
(i) appR closes and reconnects to the old `receiveFrom` of the `person.ttl`
WebSocket channel, and alice modifies once more;
(ii) appR tries to create new WebSocket and Webhook channels on `person.ttl`
and on the container.
In the `short` variant the server runs `css-<config>-short.json`
(maxDuration = 2 min). After the steps above, the run waits until 2.5 min
after subscription. alice modifies once more, and appR tries to reconnect to
the `receiveFrom`. In `default` the server runs the unchanged config, and
only the advertised expiry is recorded: 20160 min cannot be waited out within
a run.

**Procedure, variants `unsub-bob`, `unsub-anonymous`, `unsub-alice`.** Build
the scene. appR opens a fresh WebSocket channel on `person.ttl` and connects.
The named actor sends `DELETE` to the channel's id URL (bob with his DPoP
credentials; anonymous with none; alice with hers). Before that, alice (in
`unsub-alice`) tries to find the channel without being told its id: she GETs
the storage description, the subscription endpoint and `/.notifications/`,
and sends `DELETE` to the subscription endpoint. Every attempt is logged.
Then alice modifies `person.ttl`, and the run records whether appR still
receives. No revoke in these variants: they test who can end appR's channel,
not the revoke. This is recorded behaviour, not framed as an attack.

**Conditions.** p3 × {wac, acp} × {default, short, unsub-bob,
unsub-anonymous, unsub-alice}, ≥ 10 reps each.

**Predictions** (source readings cite CSS v7.2.0).
- **H3.1.** All four subscriptions succeed before the revoke. The responses
  carry `receiveFrom` (WebSocket) and an `endAt` of about subscription time +
  20160 min (default) or + 2 min (short). Source reading:
  `NotificationSubscriber.ts` clamps `endAt` to `maxDuration`, default 20160.
- **H3.2 (the central prediction).** After the revoke, appR's existing
  `person.ttl` channels keep delivering: **20/20 notifications on the
  WebSocket and 20/20 on the Webhook**, each with the full activity payload.
  This holds on WAC and ACP. Source reading: read permission is checked only
  when subscribing (`NotificationSubscriber.authorize`); the WebSocket connect
  is not authorised (`WebSocket2023Listener.ts`); and `emit` does not re-check
  (`ListeningActivityHandler.ts`).
- **H3.3.** The container channels receive no notification for the 20
  content modifications of `person.ttl` (the container's membership does not
  change). Less certain than H3.2.
- **H3.4.** **Nothing notifies appR that its access ended.** No message
  arrives on any appR channel in the 3 s after the revoke, and no later
  message refers to the ACL/ACR. The ACL/ACR is a different resource from
  `person.ttl`, and appR has no channel on it.
- **H3.5.** After the revoke, appR can reconnect to the old `receiveFrom`,
  and it receives the next modification.
- **H3.6.** After the revoke, a new subscription by appR on `person.ttl` is
  refused with **403** (both channel types, both configs). A new subscription
  on the container succeeds (appR still has Read on the container).
- **H3.7 (short).** After `endAt`, no further notification arrives on either
  channel type. The open WebSocket is **not** closed by the server within the
  observation window. Source reading: `WebSocket2023Storer.ts` sweeps expired
  sockets every 60 min. Reconnecting to the expired `receiveFrom` is refused.
- **H3.8 (unsub-*).** `DELETE` on the channel id succeeds with **205** for
  bob, for an anonymous client and for alice. After it, appR receives no
  further notification. The WebSocket is not closed by the server. Source
  reading: `NotificationUnsubscriber.ts` has no credentials check and returns
  205.
- **H3.9 (unsub-alice).** Without being told the id, alice cannot find
  appR's channel. The storage description and the subscription endpoint's
  GET describe channel *types* only, and no endpoint lists channels
  (`/.notifications/` is not 2xx). `DELETE` on the subscription endpoint does
  not end appR's channel. She needs the id from appR, out of band.
- **H3.10.** Webhook POSTs from CSS carry `Authorization: DPoP <token>` and a
  `DPoP` proof. The token's `webid` is
  `<base>/.notifications/WebhookChannel2023/webId`. Source reading:
  `WebhookEmitter.ts`.

## P4: Comunica link traversal (pre-registered before P4's first run, dry runs included)

**Client.** `@comunica/query-sparql-link-traversal-solid` **0.8.0** (own
`package.json` + lockfile in `phases/p4_comunica/`), default engine settings,
run as appR. appR authenticates with DPoP client credentials written with
`jose` 6.2.12. Every HTTP request the engine makes is logged
(`comunica_http`). One Node process per run holds the engine(s)
(`driver.mjs`).

**Query** (identical before and after), with the run container as the only
seed source:
`SELECT ?person ?name ?job WHERE { ?person schema:name ?name ; schema:jobTitle ?job . }`

**Procedure.** Build the scene. Engine e1 runs the query. alice revokes
appR on `person.ttl`, and appR's direct GET (logged) confirms 403. Then the
query runs again:
- **a:** on e1, unchanged;
- **a-invalidate:** on e1 after `e1.invalidateHttpCache()`;
- **b:** on a fresh engine e2.

**Conditions.** p4 × {wac, acp} × {a, a-invalidate, b}, ≥ 10 reps each.

**Predictions.**
- **H4.1.** Before the revoke, the query returns both fictional people
  (Tesmer Quillon from `person.ttl`, Liesel Omandyke from `distractor.ttl`).
  The engine reaches both files by following `ldp:contains` from the
  container.
- **H4.2 (a).** After the revoke, the same engine still returns **Tesmer
  Quillon**, and it makes **no** HTTP request to `person.ttl` for the second
  query. Source reading: `ActorOptimizeQueryOperationQuerySourceIdentify`
  keeps an LRU cache of identified sources keyed by source URL, cleared only
  through the HTTP invalidator. We don't predict whether the engine
  re-requests the container itself.
- **H4.3 (a-invalidate) and H4.4 (b).** After the revoke, the engine
  requests `person.ttl` again and receives 403. **Tesmer Quillon is not in
  the result.** Not predicted: whether the 403 surfaces as a query error or
  is skipped with the distractor's row still returned. The outcome records
  which one happens.
- **H4.5.** WAC and ACP give the same categorical outcome per variant.
- **H4.6.** Nothing in any response to the engine signals the revoke before
  the engine next requests `person.ttl`. The engine learns of it only through
  a 403 on a request it chooses to make.

## P5: aggregator (pre-registered before P5's first run, dry runs included)

**Aggregator** (`lib/aggregator.py`): acting as appR, it copies every triple
of `person.ttl` and `distractor.ttl` into SQLite (one row per triple, with its
source URL) at a fixed sync interval of 1 s. There are two policies:
- **naive:** a failed fetch changes nothing;
- **403-aware:** a fetch that now fails deletes that source's rows. This
  purge is **recipient-side logic written for this experiment**. It is not a
  server feature, and the server does not request it.

**Procedure.** Build the scene. Set up two comparison probes in the same
container:
- `never.ttl`, which appR is never granted;
- `scratch.ttl`, which appR can read (checked), and which alice later
  deletes.

Run 3 syncs, then alice revokes appR on `person.ttl`, then 10 more syncs.
The first post-revoke response to appR for `person.ttl` is logged in full
(status, all headers, body). Then appR GETs `never.ttl`, alice deletes
`scratch.ttl`, and appR GETs it again. The three refusals are compared on
status, body and stable headers (excluding Date, ETag, Last-Modified,
Content-Length, Keep-Alive, Connection).

**Conditions.** p5 × {wac, acp} × {naive, 403-aware}, ≥ 10 reps each.

**Predictions.**
- **H5.1.** Before the revoke, rows from both sources are copied.
- **H5.2.** The first post-revoke fetch of `person.ttl` returns **403**
  (as in P1).
- **H5.3 (naive).** All of `person.ttl`'s rows are still in the store after
  10 post-revoke syncs. This follows from the policy by construction. The
  observation is that nothing from the server removes or flags them.
- **H5.4 (403-aware).** The rows are deleted at the first sync after the
  revoke. The time from revoke to deletion is at most one sync interval plus
  one request (≲ 1.1 s).
- **H5.5 (both configs).** The three refusals ("access withdrawn",
  "never had access", "resource deleted") are **identical** to appR: the
  same status (403), the same body and the same stable headers. Nothing in
  the response tells a recipient *why* it can no longer read. The least
  certain part is the deleted resource, which could instead be 404.
- **H5.6.** appR's `distractor.ttl` rows stay in both variants (its access
  is unchanged).

## P6: agent memory (pre-registered before P6's first run, dry runs included)

**Models** (Ollama 0.34.4 on 127.0.0.1, pinned by digest in
`config/ollama-models.txt`; the run refuses a digest mismatch):
`nomic-embed-text:latest` for embeddings, `qwen2.5:3b` (Q4_K_M) for
generation. *Model choice:* the Spec names `qwen2.5:7b-instruct`; the User
chose the smaller `qwen2.5:3b` on 2026-09-24. Generation: temperature 0,
seed = the fixed run seed.

**Memory** (`lib/memory.py`), acting as appR: GET `person.ttl` and
`distractor.ttl`, split each into one chunk per top-level fact of the person
(prefixed with the person's name; 10 facts each, so 20 chunks), embed them and
store chunks + vectors in SQLite. The memory is built once, before the
revoke, and is never re-synced. That is the scenario: an agent's memory
built while access was valid.

**Procedure.** Build the scene and the memory. Ask the 10 fixed questions
(`fixtures/questions.json`, each answerable only from `person.ttl`): for each,
retrieval (top k = 4 by cosine similarity: chunk ids, scores, and whether the
chunk comes from `person.ttl`), then generation from those 4 chunks (prompt
and answer logged verbatim). alice revokes appR on `person.ttl`, and appR's
direct GET (logged) confirms the revoke. The 10 questions are asked again
with the same memory.

**Conditions.** p6 × {wac, acp} × {rag}, ≥ 10 reps each.

**Predictions.**
- **H6.1.** The memory holds 20 chunks, 10 of them from `person.ttl`, before
  and after the revoke. Nothing removes or flags them.
- **H6.2.** appR's direct GET after the revoke is 403 (as in P1).
- **H6.3 (primary).** After the revoke, for **each** of the 10 questions,
  the top 4 include the `person.ttl` chunk holding the answer. For the top-1
  chunk we predict `person.ttl` for all 10 questions. This is the least
  certain part, because a distractor chunk of the same kind (for example the
  other person's appointment) could rank first.
- **H6.4.** Retrieval is the same before and after the revoke (the same chunk
  ids in the same order), and the same across reps and configs. The config
  cannot matter once the memory is built.
- **H6.5 (secondary).** Generation after the revoke gives the correct
  fixture value (the `match` substring) for at least 8 of the 10 questions.
  The answers are the same as before the revoke. If answers vary across reps
  despite temperature 0 and a fixed seed, the variance is logged as an
  observation and not rerun. Generation correctness is kept out of the
  categorical `outcome` that `exp:compare` checks.
- **H6.6.** Nothing from the server reaches the memory. The only
  revoke-related signal appR gets is the 403 on its own direct GET, which the
  memory never makes.

## P7: withdrawal notice (pre-registered before P7's first run, dry runs included)

**Mechanism: a prototype written for this experiment, not a Solid or CSS
feature.** When alice revokes, she sends each recipient a "withdrawal notice"
to its LDN inbox (Linked Data Notifications, W3C REC 2017; `spec_quotes.md`
§8). Each recipient runs a handler that polls its own inbox.

**Recipients and their stores.** Both appR and bob are recipients in P7 (in
P1–P6 bob was the control). Before the revoke, each builds a P5 aggregator
store (policy **naive**, so any purge comes from the notice and not from a
403) and a P6 memory (chunks + embeddings, no generation) from `person.ttl`
and `distractor.ttl`. There are no syncs after the revoke.

**Inbox setup (logged as item b).** Each recipient, with its own
credentials: creates the container `<pod>ch3-inbox/` (once; it is reused
across reps, so each profile advertises exactly one inbox), adds
`<webid> ldp:inbox <…/ch3-inbox/>` to its WebID profile with an N3 Patch, and
writes the inbox's access document so that alice has **Append only** (WAC:
`acl:mode acl:Append` on the container; ACP: a policy allowing `acl:Append`
to alice). The recipient keeps full control.

**Notice payload** (JSON-LD, `application/ld+json`), built only from terms
fetched in `spec_quotes.md` §10:
- ODRL: an `odrl:Permission` whose `odrl:target` is `person.ttl`,
  `odrl:assignee` is the recipient's WebID and `odrl:action` is `odrl:read`
  (the scope: which resource, which action, whose permission);
- DPV: `dpv:hasRecipient` (the recipient) and `dpv:hasDataSubject`
  (`person.ttl#me`, the fictional person the data is about);
- time: `ch3n:withdrawnAt` (`xsd:dateTime`), and a request
  `ch3n:requests ch3n:DeleteCopiesOfTarget`. `ch3n:` =
  `https://example.org/ch3/notice#` is a **local vocabulary of this
  experiment**, because no fetched ODRL/DPV term covers a withdrawal time or a
  deletion request.

We deliberately use **no** consent-status or right-exercise term
(`dpv:ConsentWithdrawn`, `dpv:RightExerciseNotice`). Such a term would assert
a legal basis or a legal right, and that is for the legal analysis to judge.

**Procedure per rep.** Build the scene (appR and bob can read `person.ttl`).
appR opens a WebSocketChannel2023 on `person.ttl` (for item c). appR and bob
build their stores. alice records the recipient list from **her own grant
log** (item a) and reads the `.acl`/`.acr` of `person.ttl`. alice revokes
appR **and** bob on `person.ttl`, then reads the access document again. alice
probes whether she can see who holds notification subscriptions on
`person.ttl` (item c: storage description, subscription endpoint,
`/.notifications/`, searching for appR's WebID and channel id). For each
recipient, alice discovers the inbox (LDN §3.1: first the `Link rel=inbox`
header on the WebID profile, then `ldp:inbox` in its RDF), then POSTs the
notice. Handlers poll every 1 s. A **cooperating** handler deletes the
aggregator rows and memory chunks whose source is the notice's
`odrl:target`. A **non-cooperating** handler receives and logs the notice
but deletes nothing. 5 s after the last notice, the run records, per
recipient (item d): notice sent time (alice's POST response), received time
(the handler's GET of the notice), purge completed time, residual
`person.ttl` rows and chunks, and how many of the 10 P6 questions still
retrieve a `person.ttl` chunk as top-1. Then alice records **everything she
can see**: the POST status and headers, a GET of the `Location`, and a GET of
the inbox.

**Conditions.** p7 × {wac, acp} × {cooperating, non-cooperating}, ≥ 10
reps each.

**Predictions.**
- **H7.1 (b).** Inbox creation, the profile patch and the Append-only
  access document all succeed on WAC and ACP.
- **H7.2 (a).** The recipient list comes only from alice's own grant log.
  Before the revoke, the access document names appR and bob; after it,
  neither. CSS exposes no record of which agents were granted or read
  `person.ttl` once the document is rewritten.
- **H7.3 (c).** alice cannot see that appR holds a subscription on
  `person.ttl`: neither appR's WebID nor its channel id appears in any probe
  (as P3 H3.9).
- **H7.4.** Discovery: the WebID profile carries **no** `Link rel=inbox`
  header, so the header step fails and the RDF step finds `ldp:inbox`. Less
  certain.
- **H7.5.** alice's POST to each inbox returns **201** with a `Location`
  header, in both variants.
- **H7.6 (cooperating).** Every notice is received and purged within 5 s.
  Residual `person.ttl` rows = 0 and chunks = 0 for both recipients, the
  distractor rows and chunks stay, and 0 of 10 questions retrieve a
  `person.ttl` chunk as top-1. Sent → purged ≤ one poll interval plus
  processing (≲ 1.5 s).
- **H7.7 (non-cooperating).** Every notice is received. Residual = 23 rows
  and 10 chunks per recipient, and 10 of 10 questions still retrieve
  `person.ttl` as top-1. This is **by construction**, not a finding.
- **H7.8 (the measurement that matters).** What alice can see is
  **identical in both variants**: the POST is 201 with a `Location`, her GET
  of the `Location` is 403 (she has Append, not Read), and her GET of the
  inbox is 403. No acknowledgement of receipt or purge reaches her, and
  nothing lets her tell a cooperating recipient from a non-cooperating one.
  LDN's 201 means only that the notification resource was created. We add no
  acknowledgement mechanism; we record only that none exists.
- **H7.9.** WAC and ACP give the same categorical outcome per variant.

## P7 notice v2: DPV consent status (pre-registered 2026-09-29, before P7 v2's first run, dry runs included)

**Why, and a documented change of design.** The P7 section above says we
"deliberately use **no** consent-status or right-exercise term". At the
User's request (2026-09-29), the notice now also expresses the **withdrawal
of consent**, not only the revocation of access. This reverses that one
design choice, for the new variants only. The earlier P7 runs and their raw
files stay as they are, and they remain the evidence for notice v1.

**Terms** (DPV 2.3, CG-FINAL 25 February 2026, fetched live on 2026-09-29
from https://w3id.org/dpv/modules/legal_basis; identical to
`spec_quotes.md` §10):
- `dpv:hasConsentStatus` (https://w3id.org/dpv#hasConsentStatus),
  "Specifies the state or status of consent";
- `dpv:ConsentWithdrawn` (https://w3id.org/dpv#ConsentWithdrawn), "The
  state where the consent is withdrawn or revoked specifically by the data
  subject and which prevents it from being further used as a valid state";
- `dpv:Consent` (https://w3id.org/dpv#Consent), "Consent of the Data
  Subject for specified process or activity".

**Notice v2** = notice v1 unchanged (same ODRL permission, `dpv:hasRecipient`,
`dpv:hasDataSubject`, `ch3n:` terms), plus one node:

    "ch3n:withdrawnConsent": {"@type": "dpv:Consent",
                              "dpv:hasConsentStatus": {"@id": "dpv:ConsentWithdrawn"}}

`ch3n:withdrawnConsent` is a local linking term, like `ch3n:withdrawnPermission`,
because no fetched DPV term links a notice to the consent it concerns.

**A modelling mismatch, stated up front (the User's decision).** DPV's usage
note for `dpv:ConsentWithdrawn` suggests it "when it is the data subject" and
`dpv:ConsentRevoked` "when it is a non-data-subject entity". In our scene the
notice's `dpv:hasDataSubject` is `person.ttl#me` (the fictional person in the
passport-renewal fixture, which is kept), while the sender is alice. The User
chose `dpv:ConsentWithdrawn` anyway, with the mismatch recorded in
`SPEC_VS_IMPL.md`. Whether that choice fits the law is not assessed here.

**Declared only.** No server acts on these terms. CSS stores the notice body
as it stores any resource, and the prototype handlers still act on
`odrl:target` alone; they do not read the consent status.

**Conditions.** Two new variants, so the notice version is part of the
condition: p7 × {wac, acp} × {`cooperating-consent`,
`non-cooperating-consent`}, ≥ 10 reps each, in full run 1 and, after
`npm run exp:setup -- --reset`, in full run 2. The v1 variants
(`cooperating`, `non-cooperating`) keep sending notice v1. Every run logs
`notice_version` (1 or 2) in its `notice_sent` lines.

**Predictions.**
- **H7.10.** Every v2 variant gives the **same** outcome as its v1
  counterpart for H7.1–H7.9: inbox setup succeeds, recipient list only from
  alice's grant log, no subscription visible, discovery through RDF, POST
  201 + `Location`, cooperating residual 0 / non-cooperating residual 23
  rows + 10 chunks, and alice's view identical in both variants. Adding the
  consent-status node changes nothing any party does.
- **H7.11.** The notice each recipient reads back from its inbox, parsed as
  JSON-LD, contains the triple `?c dpv:hasConsentStatus dpv:ConsentWithdrawn`
  with `?c a dpv:Consent`, in every rep (new outcome field
  `notice_has_consent_status`, true for both recipients). CSS stores and
  returns the node without removing or rewriting it.
- **H7.12.** Nothing in CSS's response to alice's POST, or in anything alice
  can read afterwards, depends on the consent status: her view is
  byte-for-byte the same set of statuses and header names as with notice v1.
