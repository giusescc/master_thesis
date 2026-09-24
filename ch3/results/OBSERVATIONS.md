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
