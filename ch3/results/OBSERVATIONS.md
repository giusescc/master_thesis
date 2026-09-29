# OBSERVATIONS (Chapter 3)

Measured facts only, each linked to its raw JSONL files. Every statement is
scoped as "CSS 7.2.0 with <config> did X". Interpretation lives in
`INTERPRETATION_NOTES.md`; spec comparison in `SPEC_VS_IMPL.md`.

Timings are reported as distributions (median, p95, min–max) over all runs of
a condition.

## P1: direct path

**Ran:** full run 1, p1 × {wac, acp} × direct, 10 reps each (20 runs, 0
failed). Raw: [`raw/p1/wac/`](raw/p1/wac/) and [`raw/p1/acp/`](raw/p1/acp/).
Procedure and definitions: `HYPOTHESES.md` § P1.

Same categorical outcome in 10/10 runs per config:

| Observation | CSS 7.2.0 + WAC (:3100) | CSS 7.2.0 + ACP (:3101) |
|---|---|---|
| appR GET before the revoke | 200 | 200 |
| appR GETs sent after `revoke_done` | all 403 (≈201 per run) | all 403 (≈201 per run) |
| stale reads (2xx to a request sent after `revoke_done`) | 0 in every run | 0 in every run |
| bob (control) GETs, before, during and after | all 200 | all 200 |
| appR's access token before vs after (sha256 prefix + `exp`) | unchanged | unchanged |
| `WAC-Allow` on appR's 200 before the revoke | `user="read"` | header absent |
| `WAC-Allow` on appR's 403 after the revoke | header absent | header absent |
| `WAC-Allow` on bob's responses | `user="read"` | header absent |
| 403 body | `{"name":"ForbiddenHttpError","message":"","statusCode":403,"errorCode":"H403","details":{}}` | identical |

Timings (medians over 10 runs; min–max):

| Metric | WAC | ACP |
|---|---|---|
| time-to-denial (ms) | 38.9 (34.3–43.7) | 32.8 (28.7–38.8) |
| of which: wait from `revoke_done` to appR's next scheduled GET (ms) | 28.5–38.6 | 20.8–29.8 |
| of which: latency of that first post-revoke GET (ms) | 4.2–5.8 | 7.0–14.3 |
| alice's revoke write, request → response (ms) | 16.6 (12.5–19.1) | 23.7 (22.4–32.1) |

- **Resolution limit.** Time-to-denial is bounded below by the 50 ms polling
  cadence, and most of it is the wait for appR's next scheduled GET. The
  observed fact is categorical: in 20/20 runs, **the first GET appR sent after
  alice's revoke response had arrived was answered 403**. No request was in
  flight across `revoke_done` in any run (`straddling_requests` is empty).
  In some runs, a GET that appR sent *during* alice's revoke write (0–6 ms after
  `revoke_sent`, before `revoke_done`) was still answered 200.
- The poller skipped 0–3 of its 50 ms slots in 2 runs (`skipped_slots` in the
  summary line), because a response took longer than the interval.
- Nothing in the 403 response (status, headers, body) states why access was
  denied. H1.6 predicted this; P5 compares it with the "never had access" and
  "resource deleted" responses.
- Predictions H1.1–H1.6: all matched. H1.5 (no `WAC-Allow` under ACP) had
  already been seen in the Chunk 1 smoke test, as noted in HYPOTHESES.md.

## P2: HTTP caching

**Ran:** full run 1, p2 × {wac, acp} × {proxyA, proxyB}, 10 reps each (40
runs, 0 failed). Raw: [`raw/p2/wac/`](raw/p2/wac/), [`raw/p2/acp/`](raw/p2/acp/).
Proxy: nginx 1.28.3 in Docker (`config/nginx/IMAGE`, pinned by digest).
Config A honours origin headers. Config B is a **deliberately permissive
configuration** (every 200 stored 60 s, `Vary` ignored, URL-only cache key).
Both are proxy configurations written for this experiment, not CSS behaviour.

**Instrument correction (documented, before the accepted runs).** A first
batch (7 runs, wac/proxyA) was stopped. Two of its runs failed with a 30 s
client timeout. The CSS log shows the proxied request arriving about 36 s
after nginx sent it (e.g. sent 17:11:34, received 17:12:10 UTC). That is a
stall in Docker Desktop's container-to-host network, which occurred when
nginx opened a new upstream connection per request. Both configs were given
upstream keepalive, which does not change what is cached, and P2 was rerun.
The 7 runs stay on disk and are listed with the reason in
[`raw/EXCLUDED.tsv`](raw/EXCLUDED.tsv). They are not counted.

Same categorical outcome in 10/10 runs for every condition:

| Observation | A, WAC | A, ACP | B, WAC | B, ACP |
|---|---|---|---|---|
| origin `Cache-Control` / `Expires` on `person.ttl` | absent / absent | absent / absent | absent / absent | absent / absent |
| origin `Vary` | `Accept,Authorization,Origin` | same | same | same |
| origin `ETag`, `Last-Modified` | present | present | present | present |
| proxy status of appR's 1st / 2nd GET before the revoke | MISS / MISS | MISS / MISS | MISS / HIT | MISS / HIT |
| bob's GET before the revoke (after appR's) | 200 MISS | 200 MISS | **200 HIT** (served appR's cached copy) | **200 HIT** |
| appR direct GET after the revoke | 403 | 403 | 403 | 403 |
| appR's first GET through the proxy after the revoke | 403 MISS | 403 MISS | **200 HIT** | **200 HIT** |
| cached body served after the revoke = the fixture (sha256) | n/a | n/a | yes | yes |
| appR's proxied GETs answered 200 after the revoke (1 s polling, 70 s) | 0 | 0 | 61 of 71 | 61 of 71 |
| last proxied 200 after the revoke (ms) | n/a | n/a | 60 017–60 040 | 60 018–60 029 |
| first proxied 403 after the revoke (ms) | 14–37 | 21–46 | 61 038–61 100 | 61 054–61 126 |
| **anonymous** GET through the proxy just after the revoke | 401 | 401 | **200 HIT** | **200 HIT** |
| anonymous GET directly to CSS just after the revoke | 401 | 401 | 401 | 401 |
| anonymous GET through the proxy at the end (70 s) | 401 | 401 | 401 | 401 |
| bob through the proxy at the end | 200 | 200 | 200 | 200 |

- Under config B, the proxy served the cached fixture to appR for about 60 s
  after CSS had begun answering appR with 403. It also served it to an
  unauthenticated client, to whom CSS itself answered 401. The stale answers
  formed one block, followed only by denials (`proxy_stale_then_denied_contiguous`).
  They ended when the entry was 60 s old, not in response to anything CSS sent.
  No request to CSS in that window reached the resource (every answer was a HIT).
- Under config A, nothing was cached, because CSS 7.2.0 sent no freshness
  information for `person.ttl`. Proxied answers matched direct answers.
- CSS 7.2.0 with WAC and with ACP sent nothing to the proxy when the ACL/ACR
  changed. Predictions H2.1–H2.6: all matched.

## P3: notifications

**Ran:** full run 1, p3 × {wac, acp} × {default, short, unsub-bob,
unsub-anonymous, unsub-alice}, 10 reps each (100 runs, 0 failed). Raw:
[`raw/p3/wac/`](raw/p3/wac/), [`raw/p3/acp/`](raw/p3/acp/). Procedure:
`HYPOTHESES.md` § P3. Every notification is logged verbatim (`ws_message`,
`webhook_message`) with its arrival time.

**Instrument addition (after the dry run, before the real runs; commit
7722269).** In the `short` dry run, the WebSocket connect to the expired
`receiveFrom` was accepted, which H3.7 had not predicted. To tell whether that
socket was live, one more step was added: alice modifies `person.ttl` once
more after that reconnect. The prediction in HYPOTHESES.md was not changed.

Same categorical outcome in 10/10 runs for every condition, on WAC and on ACP
alike. Lifecycle variants (`default`, `short`):

| Observation | WAC | ACP |
|---|---|---|
| appR's 4 subscriptions (WS + Webhook, on `person.ttl` + container) | 200 | 200 |
| advertised `endAt` − subscription time | 20160 min (`default`), 2 min (`short`) | same |
| baseline modification received on the `person.ttl` channels | yes (WS and Webhook) | yes |
| any message in the 3 s after the revoke (an ACL/ACR-change signal) | none | none |
| any message, at any time, that mentions the `.acl` / `.acr` | none | none |
| notifications on appR's `person.ttl` channels for alice's 20 post-revoke modifications | **20/20 WS, 20/20 Webhook** | **20/20 WS, 20/20 Webhook** |
| notifications on the container channels for those 20 modifications | 0 (also 0 for the baseline) | 0 |
| message type | `Update` (with `object`, `state`, `published`) | same |
| appR reconnects to the old `receiveFrom` after the revoke | accepted, and it receives the next modification | same |
| appR's new subscription on `person.ttl` after the revoke (WS / Webhook) | 403 / 403 | 403 / 403 |
| appR's new subscription on the container after the revoke (WS / Webhook) | 200 / 200 | 200 / 200 |
| Webhook POSTs: token `webid` | `http://localhost:3100/.notifications/WebhookChannel2023/webId` | `…:3101/…/webId` |
| Webhook POSTs: `DPoP` proof header present | yes | yes |

Only in `short` (2-min `maxDuration`), about 2.5 min after subscribing:

| Observation | WAC | ACP |
|---|---|---|
| notification for a modification after `endAt`, on the open WS / on the Webhook | 0 / 0 | 0 / 0 |
| the open WS closed by the server by then | no | no |
| WebSocket connect to the expired `receiveFrom` | **handshake accepted** | **handshake accepted** |
| … and does that socket receive the next modification | no | no |

- **What "accepted" means here.** The client's WebSocket handshake completed
  (`ws_connect ok=true`). At the same moment CSS logged an error and never
  delivered on that socket, and did not close it within the run. One line per
  run, 10 per config, in
  [`excerpts/p3-expiry-css-log.txt`](excerpts/p3-expiry-css-log.txt), e.g.
  `[WebSocketServerConfigurator] {Primary} error: Something went wrong handling a WebSocket connection: Unknown or expired WebSocket channel http://localhost:3100/.notifications/WebSocketChannel2023/e5175abc-…`.
  The same file shows `KeyValueChannelStorage … has expired.` for each
  `person.ttl` channel when the post-expiry modification arrived (the expiry
  is checked when the channel is next looked up). From the client's side, the
  expired channel can only be told apart from a quiet live one by the absence
  of messages.
- **Delivery latency** after revoke, alice's modify response → notification
  arrival (all 40 lifecycle runs): WebSocket median 3.6 ms (0.6–59.7 ms,
  n = 800); Webhook median 5.3 ms (2.5–63.6 ms, n = 840). The last
  notification to reach appR from a channel on the revoked resource arrived
  26.5–27.0 s after the revoke in every lifecycle run. That is where the
  procedure stopped modifying, not where delivery stopped.
- The reconnects (after the revoke and after expiry) send **no credentials**.
  The `receiveFrom` URL alone was enough to receive after the revoke.
- appR's Webhook `sendTo` was `http://127.0.0.1:<port>/hook/<label>` (not
  https). CSS 7.2.0 accepted the subscriptions (200) and POSTed to it. Not
  predicted; see SPEC_VS_IMPL P3-6.
- The default 20160-min expiry is recorded from the advertised `endAt` only.
  14 days cannot be observed within a run.

Unsubscribe variants (a fresh WS channel of appR's on `person.ttl`, no revoke):

| Observation | bob | anonymous | alice |
|---|---|---|---|
| appR received before the `DELETE` | yes | yes | yes |
| `DELETE <channel id>` status (empty body) | **205** | **205** | **205** |
| appR received the next modification | no | no | no |
| appR's socket closed by the server | no | no | no |

Identical on WAC and ACP. alice's attempts to find appR's channel **without**
being told its id (`unsub-alice`, 10/10 on both configs):

| Probe by alice | Status | Contains the channel id? |
|---|---|---|
| GET her storage description `/alice/.well-known/solid` | 200 | no |
| GET the subscription endpoint `/.notifications/WebSocketChannel2023/` | 200 | no |
| GET `/.notifications/` | 400 (`BadRequestHttpError`, "… GET is not allowed.") | no |
| DELETE the subscription endpoint | 404 (`NotFoundHttpError`) | appR's channel still delivered afterwards |

She could end the channel only after its id was handed to her
(`channel_id_handed_to_alice`, a step of the procedure).

**Predictions.** H3.1–H3.6, H3.8, H3.9 and H3.10 matched on both configs.
**H3.7 was partly wrong.** Its "no further notification after `endAt`" and
"the open socket is not closed" parts matched. Its "reconnecting to the
expired `receiveFrom` is refused" part did not hold at the handshake level:
the handshake was accepted, and the socket then stayed silent (see above).
The source reading behind H3.7 (`WebSocket2023Listener.canHandle` throws for
an unknown or expired channel) is consistent with the log line. The error is
raised after the upgrade, so the client is not refused. This last point is
inferred from the log plus the observation, not traced line by line.

## P4: Comunica link traversal

**Ran:** full run 1, p4 × {wac, acp} × {a, a-invalidate, b}, 10 reps each
(60 runs, 0 failed). Raw: [`raw/p4/wac/`](raw/p4/wac/), [`raw/p4/acp/`](raw/p4/acp/).
Client: `@comunica/query-sparql-link-traversal-solid` 0.8.0, default engine
settings, as appR (`phases/p4_comunica/`, own lockfile). Every HTTP request
the engine made is in the raw files (`comunica_http`).

The categorical outcome was the same in 60/60 runs, for all three variants
and both configs:

| Observation | a (same engine) | a-invalidate | b (fresh engine) |
|---|---|---|---|
| query before the revoke | both people (Tesmer Quillon, Liesel Omandyke) | same | same |
| HTTP requests for the first query | 6 (container, `.meta`, both files, their `.meta`) | same | same |
| appR's direct GET after the revoke | 403 | 403 | 403 |
| HTTP requests for the second query | **2: container 200, then `person.ttl` 403** | same | same |
| second query result | **error, no rows** | same | same |
| revoked person in the second result | no | no | no |
| distractor person (still readable) in the second result | **no** (the query stopped before requesting `distractor.ttl`) | no | no |

The error the engine returned (verbatim, identical in all 60 runs):
`Hypermedia link resolution failed: none of the configured actors were able to resolve links from metadata` / `Error messages of failing actors:` / `Actor urn:comunica:default:rdf-resolve-hypermedia-links/actors#traverse requires a 'traverse' metadata entry.` / `Actor urn:comunica:default:rdf-resolve-hypermedia-links/actors#next requires a 'next' metadata entry.`
The message does not mention the 403, access, or `person.ttl`.

- **The same engine instance re-requested the container and `person.ttl` for
  the second query.** It did not answer from anything kept from the first query.
  So `invalidateHttpCache()` (a-invalidate) and a fresh engine (b) made no
  observable difference in this setup.
- With default settings, one 403 during traversal made the whole query fail.
  Rows the engine could still read (the distractor) were not returned either.
- **Predictions.** **H4.2 was wrong.** It predicted that engine `a` would
  return Tesmer Quillon without requesting `person.ttl`. The source reading
  behind it (an LRU cache of identified sources in
  `ActorOptimizeQueryOperationQuerySourceIdentify`) does not describe what
  this engine did for a link-traversal query seeded with a container. Why
  was not traced in the Comunica source. H4.1, H4.3, H4.4 and H4.5 matched.
  For H4.3/H4.4, the open point resolved as "query error, no rows" (not
  "403 skipped, distractor returned"). H4.6 matched: the engine learned of the
  revoke only from the 403 on its own request.
- Scope: one engine version, default configuration, one query shape. A
  configuration that tolerates failed links (lenient mode) was not run. It
  would be a new condition, and it was not pre-registered.

## P5: aggregator

**Ran:** full run 1, p5 × {wac, acp} × {naive, 403-aware}, 10 reps each (40
runs, 0 failed). Raw: [`raw/p5/wac/`](raw/p5/wac/), [`raw/p5/acp/`](raw/p5/acp/).
The aggregator (`lib/aggregator.py`) copies appR-readable triples into SQLite
every 1 s. The 403-aware purge is **recipient-side logic written for this
experiment**, not a server feature.

**Instrument change (after the dry run, before the real runs; commit
d908c14).** The refusal comparison first reported the three refusals as "not
identical". The only difference was each resource's own URL inside its
`Link` header (`<…/person.ttl.acl>` vs `<…/never.ttl.acl>`). The comparison
now replaces the requested URL with `<self>`. The raw responses are logged
unmodified.

Same categorical outcome in 10/10 runs for every condition:

| Observation | naive, WAC | naive, ACP | 403-aware, WAC | 403-aware, ACP |
|---|---|---|---|---|
| `person.ttl` rows copied before the revoke | 23 | 23 | 23 | 23 |
| first post-revoke fetch of `person.ttl` | 403 | 403 | 403 | 403 |
| `person.ttl` rows left after 10 post-revoke syncs | **23** (all) | **23** | 0 | 0 |
| `distractor.ttl` rows (access unchanged) | 23 | 23 | 23 | 23 |
| revoke → rows deleted (ms), median (min–max) | n/a | n/a | 21.1 (13.2–35.1) | 24.8 (21.6–46.8) |

- **Naive:** the rows stayed by construction (the policy keeps rows on a
  failed fetch). The observation is that nothing from the server removed or
  flagged them. The only change appR saw was the 403 on its next fetch.
- **403-aware:** the rows went at the first sync after the revoke, because
  our code deletes them on a non-2xx. The latency is that of one request.

**The three refusals appR can compare** (post-revoke `person.ttl`;
`never.ttl`, which appR was never granted; `scratch.ttl`, which appR could
read and alice then deleted). In 40/40 runs, on WAC and on ACP:

| | withdrawn | never had access | deleted |
|---|---|---|---|
| status | 403 | 403 | 403 |
| body (`Accept: text/turtle`) | identical | identical | identical |
| stable headers (with the requested URL normalised) | identical | identical | identical |

The body, verbatim, in all 120 refusals: `<b0> <http://purl.org/dc/terms/title> "ForbiddenHttpError";` / `<http://purl.org/dc/terms/description> "".`
Header names present: `accept-ranges`, `access-control-allow-credentials`,
`access-control-allow-origin`, `access-control-expose-headers`,
`content-type`, `link`, `transfer-encoding`, `vary`, `x-powered-by`. The
`Link` header names the resource's own `.meta` and `.acl`, and it does so for
the deleted resource too.

- Nothing in the response lets appR tell "access withdrawn" from "never had
  access" or from "resource deleted". The deleted resource answered 403, not
  404, to appR, who had no Read on the container's members. (CLAUDE.md
  already records that CSS gives the owner 404 there.)
- Predictions H5.1–H5.6: all matched. H5.5's least certain part (deleted →
  possibly 404) resolved as 403.

## P6: agent memory

**Ran:** full run 1, p6 × {wac, acp} × rag, 10 reps each (20 runs, 0
failed). Raw: [`raw/p6/wac/`](raw/p6/wac/), [`raw/p6/acp/`](raw/p6/acp/).
Models: Ollama 0.34.4, `nomic-embed-text:latest` (`0a109f42…`) and
`qwen2.5:3b` Q4_K_M (`357c53fb…`), pinned in
[`../config/ollama-models.txt`](../config/ollama-models.txt), checked at the
start of every run (`models` line). Generation used temperature 0 and seed
= the run seed. The memory is recipient-side code written for this
experiment (`lib/memory.py`). It was built once, while appR could read, and
never re-synced.

**Instrument addition (after the first dry run, before the real runs; commit
1b30b05).** The rank of the chunk that holds each answer is now logged
(`after_answer_chunk_rank`). "Some top-k chunk comes from `person.ttl`" was
weaker than what H6.3 predicts.

Same categorical outcome in 10/10 runs per config, identical on WAC and ACP:

| Observation | WAC | ACP |
|---|---|---|
| chunks in the memory from `person.ttl`, before / after the revoke | 10 / 10 | 10 / 10 |
| chunks in total after the revoke | 20 | 20 |
| appR's direct GET of `person.ttl` after the revoke | 403 | 403 |
| questions (of 10) whose top-1 chunk is from `person.ttl`, after the revoke | **10** | **10** |
| questions whose answer-holding `person.ttl` chunk is in the top 4 | **10** (rank 1 for 9; rank 2 for F03) | same |
| retrieval before vs after the revoke (ids, order, scores) | identical | identical |
| generated answers containing the fixture value, before / after (secondary) | 10 / 10 in every run | 10 / 10 |

- F03 ("Who is Tesmer Quillon's employer?"): the top-1 chunk was the
  `employeeId` chunk (`person.ttl#c04`), and the `worksFor` chunk that holds
  the answer was rank 2. For F07 and F10, the 4th hit was the distractor's
  chunk of the same kind. All other hits were `person.ttl` chunks.
- **Variance across reps (secondary evidence):** none. Over all 20 runs, each
  question produced exactly one distinct answer text, one score tuple and one
  ranking after the revoke. Answers before and after the revoke were
  identical in every run (10/10).
- Answers after the revoke, verbatim (the same in every run), e.g. F01
  `Tesmer Quillon's home address is Gruenmattweg 173, Lindwil, with a postal code of 9107.`;
  F06 `Tesmer Quillon's employee ID is QI-58213.`; F09 `Oriane Pelletaz`.
  All 10 answers and their prompts are in each run's `generation` lines.
- Nothing from CSS reached the memory. The 403 went to a direct GET that the
  memory itself never makes.
- **Predictions:** H6.1–H6.6 all matched. H6.3's least certain part (top-1
  from `person.ttl` for every question) held. The answer-holding chunk was
  not top-1 for F03, and H6.3 predicted only "in the top 4" for that.

## P7: withdrawal notice

**Ran:** full run 1, p7 × {wac, acp} × {cooperating, non-cooperating}, 10
reps each (40 runs, 0 failed). Raw: [`raw/p7/wac/`](raw/p7/wac/),
[`raw/p7/acp/`](raw/p7/acp/). The notice, the handlers and the purge are a
**prototype written for this experiment**, not a Solid or CSS feature. Both
appR and bob are recipients in P7. Both build a P5 aggregator store
(policy naive) and a P6 memory before the revoke. Every notice is logged
verbatim (`notice_sent`, `notice_received`).

Same categorical outcome in 10/10 runs for every condition, identical on WAC
and ACP.

**(a) Where alice's recipient list comes from.** From **her own grant log**
(the `grant` lines the run wrote), logged as `recipient_list` with
`server_exposed=false`. Reading `person.ttl`'s access document: before the
revoke it names appR and bob; after the revoke it names **neither**. After
the revoke, nothing alice can read on CSS 7.2.0 names the former recipients.

**(b) The inbox setup each recipient needed.** Each recipient has a
container `<pod>ch3-inbox/`. It was created (201) during the P7 dry runs and
already existed in all 80 setups of full run 1 (full run 2: see § "Full run 2"). In every run, each recipient added
`ldp:inbox` to its WebID profile with an N3 Patch (205), and rewrote the
inbox's access document so that alice has **`acl:Append` only** (WAC `.acl`,
ACP `.acr`: 205 in 80/80). The recipient keeps full control. The full documents are in the
`inbox_setup` lines. Discovery by alice: the profile's `HEAD` response
carried **no** `Link rel=inbox` header in any run, and the `ldp:inbox` triple
in the profile's RDF gave the inbox.

**(c) Can alice see who holds notification subscriptions on her resource?**
**No**, in 40/40 runs. appR held a WebSocket channel on `person.ttl`. Neither
appR's WebID nor the channel id appeared in her storage description (200),
the subscription endpoint (200) or `/.notifications/` (400). This repeats P3.

**(d) Per recipient** (medians over 10 runs; min–max):

| | cooperating, WAC | cooperating, ACP | non-cooperating, WAC | non-cooperating, ACP |
|---|---|---|---|---|
| notice received by the handler | yes (appR, bob) | yes | yes | yes |
| sent → received (ms), appR | 977 (909–1018) | 956 (839–976) | 980 (916–993) | 973 (913–1072) |
| sent → purge completed (ms), appR | 978 (911–1019) | 956 (842–978) | n/a | n/a |
| residual `person.ttl` rows / chunks, each recipient | **0 / 0** | **0 / 0** | 23 / 10 | 23 / 10 |
| distractor rows / chunks kept | 23 / 10 | 23 / 10 | 23 / 10 | 23 / 10 |
| questions (of 10) still retrieving `person.ttl` as top-1 | 0 | 0 | 10 | 10 |

bob's timings are within the same ranges (raw `summary` metrics). The
sent → received time is set by the handler's 1 s polling, and in this
procedure it came out close to a full interval. It is a property of our
handler, not of CSS. The non-cooperating residual is **by construction**
(that handler was written not to purge). It is not a finding.

**What alice can see: identical in both variants.** For each recipient, in
40/40 runs:

| alice's observation | cooperating | non-cooperating |
|---|---|---|
| POST of the notice to the inbox | 201, `Location` set, empty body | same |
| response header names (Date, Location, Content-Length, Keep-Alive, Connection set aside) | accept-ranges, access-control-allow-credentials, access-control-allow-origin, access-control-expose-headers, link, transfer-encoding, vary, x-powered-by | same |
| her GET of the `Location` (the stored notice) | 403 | 403 |
| her GET of the inbox | 403 | 403 |
| any message back to alice | none | none |

Nothing alice received distinguished a recipient that deleted its copies
from one that kept them. No acknowledgement mechanism was added, and none
exists in this setup. The mechanism cannot tell alice whether a notice was
acted on, and it cannot reach a recipient that is not in her own grant log
or that has no inbox.

**Predictions:** H7.1–H7.9 all matched. H7.4 (no `Link rel=inbox` on the
profile) was the less certain one, and it held.

## P7 rerun: notice v2 with a DPV consent status

**Why.** At the User's request (2026-09-29), the notice should express the
withdrawal of consent, not only the revocation of access. Notice v2 is
notice v1 unchanged plus one node, `ch3n:withdrawnConsent`: a `dpv:Consent`
with `dpv:hasConsentStatus dpv:ConsentWithdrawn` (DPV 2.3, fetched live
2026-09-29; quoted in `SPEC_VS_IMPL.md` P7-6). Predictions H7.10–H7.12 were
committed first (932b9f6), and the first raw file came after (567915a). The
passport-renewal fixture is unchanged.

**Which runs used which notice.** The notice version is part of the
condition. `cooperating` and `non-cooperating` are **notice v1** (the 80
raw files of 2026-09-28, all kept and still counted).
`cooperating-consent` and `non-cooperating-consent` are **notice v2**, and
every one of their `notice_sent` lines carries `notice_version: 2`.

**Ran:** p7 × {wac, acp} × {cooperating-consent, non-cooperating-consent},
10 reps each, in full run 1 (CH3_FULL_RUN=1) and again in full run 2 after
`npm run exp:setup -- --reset` (CH3_FULL_RUN=2): 80 runs, 0 failed, all
under `caffeinate -dis` with the lid open. No run spanned a system suspend
(max wall-minus-monotonic gap 0 s). `exp:check` and `exp:compare` exit 0
over all 36 conditions. The recipients' inboxes were created (201) by the
dry runs before full run 1, and again by the first rep of each config in full
run 2 (`cooperating-consent-r01`, WAC and ACP), since `--reset` had removed
them.

**Result: nothing any party did changed.** In every condition and both full
runs, the categorical outcome of the v2 variant, with the new field set
aside, equals that of its v1 counterpart: same inbox setup, recipient list
only from alice's grant log, no subscription visible to alice, discovery
through the profile's RDF, POST 201 + `Location`, cooperating residual
0 rows / 0 chunks and non-cooperating residual 23 rows / 10 chunks, and
alice's view (statuses and response header names) identical in both
variants. The cooperating handler acted on `odrl:target` alone, as
designed. It never read the consent status.

**The consent status survived storage.** The notice each recipient read
back from its inbox, parsed as JSON-LD, contained `?c a dpv:Consent;
dpv:hasConsentStatus dpv:ConsentWithdrawn` in 160/160 receptions (2
recipients × 80 runs; outcome field `notice_has_consent_status`). CSS
returned the JSON-LD body as it was POSTed.

**Timings** (full run 1, medians; min–max), from the handler's 1 s
polling as in v1:

| | cooperating, WAC | cooperating, ACP | non-cooperating, WAC | non-cooperating, ACP |
|---|---|---|---|---|
| sent → received (ms), appR | 970 (909–1007) | 955 (558–1013) | 982 (886–1014) | 993 (918–1124) |
| sent → purge completed (ms), appR | 972 (911–1009) | 958 (562–1015) | n/a | n/a |

**Declared only.** The DPV terms are metadata inside a notice. No server
acts on them: CSS stored the body like any other resource, and the only
thing that deleted anything was our cooperating handler, which ignores
them. A recipient that ignored the notice kept everything, whatever the
notice said about consent.

**A modelling mismatch, kept on purpose (the User's decision).** DPV's
usage note reserves `dpv:ConsentWithdrawn` for withdrawal by the data
subject. In our notice the declared data subject is `person.ttl#me` (the
fictional person in the fixture), while the sender is alice. See
`SPEC_VS_IMPL.md` P7-6.

**Predictions:** H7.10 and H7.11 matched. H7.12 matched as measured: the
outcome compares alice's statuses and response header names, not raw
bytes. The pre-registered wording "byte-for-byte" was imprecise. What was
compared is the set of statuses and header names that the same sentence
names.

## Full run 2

**Ran:** every condition again, full_run=2, from a fresh `npm run exp:setup
-- --reset` on 2026-09-28 (32 conditions, P1–P7, WAC and ACP). With the
make-up reps below, each condition has 10 completed, counted runs (320 runs,
0 failed). `npm run exp:check` exits 0.

**Result:** `npm run exp:compare` exits 0. For all 32 conditions, the set of
categorical `outcome` values in full run 2 equals the set in full run 1 (one
distinct outcome per condition in both runs), and the sha256 manifest shows no
raw file changed after it was written.

**Runs excluded: 15, hit by a system suspend.** During full run 2 the Mac
went into clamshell sleep several times (macOS `pmset` log, 2026-09-28). A
suspend freezes the process's monotonic clock but not the wall clock, so any
timed window in such a run (poll intervals, 10 s observation windows, expiry
waits) is invalid. `exp:check` now flags every run whose wall-clock span
exceeds its monotonic span by more than 5 s. 15 run-2 files crossed that
threshold (gaps from 13.5 s to 3172.0 s) in p3/acp/{short, unsub-anonymous,
unsub-alice ×2}, p4/wac/b, p5/acp/403-aware, p5/wac/{naive ×3, 403-aware}
and p6/wac/rag ×5. They are kept on disk and listed with their gap in
`raw/EXCLUDED.tsv`, never deleted. Where they completed, their categorical
outcome matched full run 1 anyway. The criterion was added after these runs
happened, as an instrument correction (commit 51983dd). It is not a finding
about CSS.

**One of them failed:** `p4/wac/20260928T120609.411Z-b-r05.jsonl`. CSS
returned HTTP 500 `Lock expired after 6000ms` on the token endpoint, just
after a 143.1 s suspend. We **infer** that the suspend caused it (the lock
timer ran out while the process was frozen). This was not reproduced and is
not proven. No other run, in either full run, hit this error.

**Make-up reps.** Each excluded run was replaced by a new rep with a new rep
number (r11 and up, `--start-rep 11`, CH3_FULL_RUN=2), run under
`caffeinate -dis` with the lid open: p3/acp/short r11 (commit 57a2b0d) and 14
more (commit bcd0031). All completed with no failure. The p3/acp/short r11 file
was first committed while still being written (647120e, labelled WIP); 57a2b0d
holds the complete file, and that is the version recorded in the manifest.

**P7 inbox setup after the reset.** Because full run 2 started from
`--reset`, the recipients' `ch3-inbox/` containers no longer existed. They
were created (201) in the first rep of each config (`cooperating-r01`, WAC and
ACP; appR and bob each: 4 creations). They already existed in the other 76 of
80 setups. The categorical outcome was unchanged.

**Timings.** The distributions in the phase sections above come from full run
1 only. Full run 2 is used for the categorical comparison, not to widen the
timing distributions.
