# Chapter 3: revocation half-life

After alice revokes a recipient's read access to a pod resource, what
persists, where, for how long, and does any component receive a signal that
access ended? Measured on **CSS 7.2.0** with two configurations: WAC on
:3100 and ACP on :3101, both on the file backend with notifications enabled.
Every claim is scoped as "CSS 7.2.0 with <config> did X".

- Predictions, committed before each phase ran: [`HYPOTHESES.md`](HYPOTHESES.md)
- Measured facts only: [`results/OBSERVATIONS.md`](results/OBSERVATIONS.md)
- Spec vs implementation, with verbatim quotes: [`results/SPEC_VS_IMPL.md`](results/SPEC_VS_IMPL.md)
- Labelled notes for the legal analysis: [`results/INTERPRETATION_NOTES.md`](results/INTERPRETATION_NOTES.md)
- Versions of everything: [`results/ENVIRONMENT.md`](results/ENVIRONMENT.md)

## Reproduce from a clean machine

Tested on macOS (Apple silicon). Localhost only: nothing talks to a
third-party pod or server.

**Prerequisites**

| Tool | Version | Why |
|---|---|---|
| Node.js | `22.23.2` (`.nvmrc`; e.g. `nvm install && nvm use`) | CSS 7.2.0 (pinned in `package-lock.json`), the P4 Comunica driver |
| uv | any recent; it installs Python 3.12 from `.python-version` | every phase runner |
| Docker | a running daemon | P2 only: nginx, pinned by digest in `config/nginx/IMAGE` (pulled on first use) |
| Ollama | `0.34.4` (e.g. `brew install ollama && brew services start ollama`) | P6, P7 |
| Ollama models | `ollama pull qwen2.5:3b` and `ollama pull nomic-embed-text` | P6, P7. The digests must match `config/ollama-models.txt`, or P6/P7 refuse to run |

**Run**

```bash
npm run exp:setup -- --reset   # npm ci + uv sync; CSS 7.2.0 WAC :3100 + ACP :3101, seeded
                               # (alice, appr, bob); client credentials into ch3/.state/.env;
                               # writes results/ENVIRONMENT.md
npm run exp:p1                 # ... through exp:p7; each runs >= 10 reps per condition on both configs
npm run exp:check              # exit 0 iff every condition has >= 10 completed runs per full run,
                               # every line has an ISO 8601 UTC ms timestamp, every raw file matches
                               # its MANIFEST.sha256 entry, and no counted run spanned a system
                               # suspend (wall clock > monotonic clock by more than 5 s)
CH3_FULL_RUN=2 npm run exp:p1  # ... a second full run (from a fresh exp:setup -- --reset)
npm run exp:compare            # exit 0 iff full runs 1 and 2 give identical categorical outcomes
                               # per condition and no raw file changed (MANIFEST.sha256)
npm run exp:stop
```

Every phase takes `-- --config wac|acp`, `--variant <v>`, `--reps N`,
`--start-rep N` (a make-up rep) and `--dry-run` (writes to
`results/scratch/`, git-ignored, never counted). Run one phase at a time:
they share the servers, and P3's `short` variant restarts them.

Approximate durations for one full run: P1 4 min, P2 50 min, P3 75 min,
P4 2 min, P5 10 min, P6 11 min, P7 10 min.

## Phases and expected outputs

Raw output: `results/raw/<phase>/<config>/<run-id>.jsonl`, one file per rep.
Files are opened with `O_EXCL` and never overwritten, and each is added to
`results/raw/MANIFEST.sha256` when it closes. Each file starts with
`run_start` (seed, full run, git commit) and ends with a `summary` line.
The summary holds the categorical `outcome` (compared across full runs) and
`metrics` (timings, distributions only). The outcomes below are those of
full run 1 (10/10 identical per condition); see OBSERVATIONS.md for details.

| Phase | Conditions (× wac, acp) | Expected outcome (full run 1) |
|---|---|---|
| **P1** direct path | `direct` | appR's first GET after the revoke is 403; bob (control) always 200. Time-to-denial: medians 32.8 ms (ACP) and 38.9 ms (WAC), range 28.7–43.7 ms (bounded by the 50 ms poll) |
| **P2** HTTP caching | `proxyA`, `proxyB` | CSS sends no Cache-Control. Proxy A (honours origin) caches nothing. Proxy B (**deliberately permissive**) serves the revoked fixture for ~60 s, also to an anonymous client |
| **P3** notifications | `default`, `short`, `unsub-bob`, `unsub-anonymous`, `unsub-alice` | Existing channels deliver 20/20 after the revoke; no ACL-change signal; new subscription 403; DELETE by anyone 205; after a 2-min expiry the handshake is accepted but silent |
| **P4** Comunica 0.8.0 | `a`, `a-invalidate`, `b` | Every engine re-requests `person.ttl` (403) and the query fails as a whole |
| **P5** aggregator | `naive`, `403-aware` | Naive keeps 23/23 rows; 403-aware deletes them after a median of ~21–25 ms (max ~47 ms); "withdrawn", "never granted" and "deleted" give identical 403s |
| **P6** agent memory | `rag` | The pre-revoke memory still retrieves `person.ttl` as top-1 for 10/10 questions and answers 10/10 correctly |
| **P7** withdrawal notice | `cooperating`, `non-cooperating` | Notice (LDN, ODRL + DPV) received in ~1 s; cooperating purges all, non-cooperating nothing (by construction); alice's view is identical either way |

## Layout

```
ch3/
  config/        css-wac.json, css-acp.json, *-short.json (maxDuration 2 min), seed.json,
                 nginx/ (configs A, B + pinned IMAGE), ollama-models.txt (pinned digests)
  fixtures/      person.ttl (revoked), distractor.ttl (kept), questions.json (P6/P7)
  lib/           env, agents (DPoP via solidlib), access (WAC/ACP), scene, jsonl, harness,
                 conditions, poll, proxy, notify, aggregator, memory
  phases/        p1_direct … p7_withdrawal (run.py each); p4_comunica/ has its own package.json
  tools/         setup.sh, provision, environment, check, compare, summarize, rawindex
  docs/          spec_quotes.md: every spec and source quote, fetched, with retrieval notes
  results/
    raw/<phase>/<config>/<run-id>.jsonl   never overwritten; MANIFEST.sha256; EXCLUDED.tsv
    excerpts/    committed server-log excerpts cited in OBSERVATIONS.md
    environment/ one ENVIRONMENT snapshot per setup
    ENVIRONMENT.md, OBSERVATIONS.md, INTERPRETATION_NOTES.md, SPEC_VS_IMPL.md
  HYPOTHESES.md  pre-registered, one commit per phase before its first run
```

State (`ch3/.state/`: pod data, credentials, server logs, P5–P7 stores) is
git-ignored. Chapter 2's lab on :3000–3002 is independent and untouched.

## Things to know

- The fixture is a fictional person with 10 invented facts. Its appointment
  is a **passport renewal**, not a medical one, to avoid health data.
- P6/P7 use `qwen2.5:3b` (chosen over the Spec's `7b` by the User).
  Retrieval, the primary measurement, does not depend on the generator.
- Instrument changes made after a dry run are documented in OBSERVATIONS.md
  with their commits. Two groups of files are excluded (kept on disk, not
  counted), each listed with its reason in `results/raw/EXCLUDED.tsv`: the 7
  runs of the P2 instrument-correction batch (OBSERVATIONS § P2), and 15 full
  run 2 runs that spanned a system suspend, one of them the P4 run that failed
  with a CSS 500 (OBSERVATIONS § "Full run 2").
