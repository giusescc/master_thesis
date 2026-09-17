# Outcome — prompt 01 (initial brief)

## Provenance

| | |
|---|---|
| Date | 2026-09-17 |
| Assistant | Claude Opus 5, via Claude Code |
| CSS | 7.2.0 · Node v22.23.2 |
| Python | 3.12.13 (via uv) |
| Repo state | empty repository, first commit made in response to this prompt |

## What the author decided

The assistant was asked to grill the author before building. It ran **seven
rounds of multiple-choice questions (26 decisions in total)**. Every design
decision below was chosen by the author, not the assistant:

- Build experiments 00–03 now; defer `04_continuous_access` (DMA 6(9)) and
  `05_onward_sharing` (Data Act Art. 5) pending review.
- Migrate **both** verbatim and with links rewritten, and compare.
- Push the ODRL experiment to prohibition-flip + voluntary policy-aware client
  + purpose-header demonstration.
- Keep `RESULTS.md` at technical findings plus "bears on" legal hooks, as open
  questions — **no legal conclusions**.
- Bob's copy goes both to local disk and into his own pod (pod as headline).
- Test identity portability, including a redirect/tombstone attempt.
- Realistic-small dataset; test whether an already-issued token survives
  revocation.
- Four-state result model with expectations declared in code.
- One branch, one PR; prompt archive with outcomes and version provenance;
  self-cleaning experiments plus `./start.sh --reset`.
- Show each result table and continue, hard-stopping only on `UNEXPECTED`.
- Figures produced only after the runs; wipe pod A and re-verify.
- Policy in the description resource (sibling as fallback); vendor and fix the
  auth library; assert on `WAC-Allow` throughout; **cite** the ODRL enforcement
  research rather than running it.
- Provider-independent WebID hosted on a real third origin; fictional data with
  a generated image; verify legal text against EUR-Lex *and* flag it;
  `uv` with Python 3.12 pinned.

> **AI-use disclosure.** The author's answers to these planning questions were
> made **with advice from a separate Claude chat session**. The decisions are the
> author's; the advice informing them was partly AI-generated.

## What the assistant produced

- `solidlib/` — the client library (DPoP auth, CSS account API, WAC,
  description resources, evidence logging, four-state checks).
- `start.sh`, `scripts/seed.py`, `scripts/webid_host.py`.
- Experiments 00–03, each with pre-registered hypotheses committed before the
  code ran.
- `figures/*.svg` — **AI-generated**, drawn after the runs from observed results.
- `RESULTS.md`, `CLAUDE.md`, `README.md`.

## Corrections made during this work

1. The brief cited Solid Protocol **§4.3.1** for description resources; the
   correct section is **§4.3.2** (§4.3.1 is Web Access Control).
2. The brief asked to install `SolidClientCredentials`. Research found it
   dormant (last commit 2025-03-05), documenting CSS 5.x, and omitting the
   RFC 9449 `ath` claim. On the author's instruction it was **vendored and
   fixed** rather than depended upon (MIT, attributed).
3. `npx @solid/community-server` floats; pinned to **7.2.0** for reproducibility.
