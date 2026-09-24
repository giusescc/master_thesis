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
